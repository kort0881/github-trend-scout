from __future__ import annotations

import json
import logging
import time

logger = logging.getLogger(__name__)

RETRY_DELAY = 20
JSON_RETRY_DELAY = 2


class LLMError(RuntimeError):
    pass


def _is_daily_quota(exc: Exception) -> bool:
    text = str(exc).lower()
    return "per day" in text or "tpd" in text


def _is_model_missing(exc: Exception) -> bool:
    text = str(exc)
    return "model_not_found" in text or "does not exist" in text or "decommissioned" in text


def _is_json_rejected(exc: Exception) -> bool:
    text = str(exc)
    return "json_validate_failed" in text or "Failed to validate JSON" in text


def _is_rate_limit(exc: Exception) -> bool:
    text = str(exc)
    return "RateLimit" in type(exc).__name__ or "429" in text or "rate_limit" in text


class GroqLLM:
    """Обёртка над Groq SDK.

    Groq выводит модели из каталога (так ушла llama-3.3-70b-versatile) и строго
    валидирует JSON, поэтому перебор идёт по двум осям: модель и режим
    (строгий json_object / обычный текст с разбором). Ошибки собираются по всем
    попыткам — иначе настоящая причина (json_validate_failed) терялась за 404
    от резервной модели.
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        fallbacks: list[str] | None = None,
        max_retries: int = 3,
    ):
        from groq import Groq

        self.client = Groq(api_key=api_key)
        self.models = [model] + [m for m in (fallbacks or []) if m and m != model]
        self.max_retries = max_retries

    @property
    def model(self) -> str:
        return self.models[0]

    def _request(self, model: str, messages: list[dict], *, json_mode: bool, temperature: float, max_tokens: int) -> str:
        kwargs: dict = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        # gpt-oss тратит бюджет на reasoning: без low-режима ответ обрезается и JSON невалиден
        if model.startswith("openai/gpt-oss"):
            kwargs["reasoning_effort"] = "low"
        resp = self.client.chat.completions.create(**kwargs)
        content = (resp.choices[0].message.content or "").strip()
        if not content:
            raise ValueError(f"{model}: пустой ответ (бюджет токенов ушёл в reasoning?)")
        return content

    def _call(self, model: str, messages: list[dict], *, json_mode: bool, temperature: float, max_tokens: int) -> str:
        """Один вызов модели с повторами только на rate-limit/сетевых ошибках."""
        last_exc: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                return self._request(
                    model, messages, json_mode=json_mode, temperature=temperature, max_tokens=max_tokens
                )
            except Exception as exc:  # noqa: BLE001 - SDK-исключения различаются по версиям
                last_exc = exc
                if _is_model_missing(exc) or _is_json_rejected(exc):
                    raise
                if attempt == self.max_retries:
                    break
                delay = RETRY_DELAY if _is_rate_limit(exc) else 5
                logger.warning(
                    "Groq %s на %s (попытка %s/%s): %s — пауза %ss",
                    "rate-limit" if _is_rate_limit(exc) else "ошибка",
                    model,
                    attempt,
                    self.max_retries,
                    str(exc)[:200],
                    delay,
                )
                time.sleep(delay)
        raise LLMError(f"{model}: {last_exc}")

    def complete(
        self,
        system: str,
        user: str,
        *,
        json_mode: bool = False,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> str:
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        errors: list[str] = []
        for model in self.models:
            try:
                text = self._call(model, messages, json_mode=json_mode, temperature=temperature, max_tokens=max_tokens)
                if model != self.models[0]:
                    logger.warning("Groq: работаю на резервной модели %s", model)
                return text
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{model}{'/json' if json_mode else ''}: {str(exc)[:160]}")
                if _is_model_missing(exc):
                    logger.warning("Groq: модели %s нет в каталоге, пробую следующую", model)
                    continue
                if json_mode and _is_json_rejected(exc):
                    try:
                        return self._call(
                            model, messages, json_mode=False, temperature=temperature, max_tokens=max_tokens
                        )
                    except Exception as inner:  # noqa: BLE001
                        errors.append(f"{model}/plain: {str(inner)[:160]}")
                continue
        raise LLMError("Groq недоступен: " + " | ".join(errors))

    def complete_json(self, system: str, user: str, *, temperature: float = 0.2, max_tokens: int = 1500) -> dict:
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        errors: list[str] = []
        for model in self.models:
            for json_mode in (True, False):
                try:
                    text = self._call(
                        model, messages, json_mode=json_mode, temperature=temperature, max_tokens=max_tokens
                    )
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"{model}{'/json' if json_mode else ''}: {str(exc)[:140]}")
                    if _is_model_missing(exc):
                        break
                    continue
                try:
                    data = parse_json_object(text)
                except ValueError as exc:
                    errors.append(f"{model}{'/json' if json_mode else ''}: {exc}")
                    time.sleep(JSON_RETRY_DELAY)
                    continue
                if model != self.models[0] or not json_mode:
                    logger.info("Groq: ответ получен на %s (json_mode=%s)", model, json_mode)
                return data
        raise LLMError("Groq недоступен: " + " | ".join(errors))


def parse_json_object(text: str) -> dict:
    """Терпимый парсер: снимает ```json-обёртки и выцепляет первый объект."""
    if not text or not text.strip():
        raise ValueError("пустой ответ модели")
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1] if cleaned.count("```") >= 2 else cleaned.strip("`")
        if cleaned.lstrip().lower().startswith("json"):
            cleaned = cleaned.lstrip()[4:]
    cleaned = cleaned.strip()
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start == -1 or end <= start:
            raise ValueError("в ответе нет JSON-объекта") from None
        data = json.loads(cleaned[start : end + 1])
    if not isinstance(data, dict):
        raise ValueError("ожидался JSON-объект")
    return data
