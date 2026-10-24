from __future__ import annotations

import json
import logging
import time

logger = logging.getLogger(__name__)

RETRY_DELAY = 30


class LLMError(RuntimeError):
    pass


class GroqLLM:
    """Обёртка над Groq SDK: json_object и текст, backoff на rate-limit, фолбэк по моделям.

    Groq выводит модели из каталога (так ушла llama-3.3-70b-versatile), поэтому
    список моделей — цепочка: при model_not_found переключаемся на следующую.
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

    def complete(
        self,
        system: str,
        user: str,
        *,
        json_mode: bool = False,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> str:
        last_exc: Exception | None = None
        for model in list(self.models):
            kwargs: dict = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}

            for attempt in range(1, self.max_retries + 1):
                try:
                    resp = self.client.chat.completions.create(**kwargs)
                    if model != self.models[0]:
                        logger.warning("Groq: работаю на резервной модели %s", model)
                    return (resp.choices[0].message.content or "").strip()
                except Exception as exc:  # noqa: BLE001 - SDK-исключения различаются по версиям
                    last_exc = exc
                    text = str(exc)
                    if "model_not_found" in text or "does not exist" in text:
                        logger.warning("Groq: модели %s нет в каталоге, пробую следующую", model)
                        break
                    rate_limited = "RateLimit" in type(exc).__name__ or "429" in text
                    logger.warning(
                        "Groq %s на %s (попытка %s/%s): %s",
                        "rate-limit" if rate_limited else "ошибка",
                        model,
                        attempt,
                        self.max_retries,
                        text[:300],
                    )
                    if attempt == self.max_retries:
                        break
                    time.sleep(RETRY_DELAY if rate_limited else 5)
        raise LLMError(f"Groq недоступен на моделях {self.models}: {last_exc}")

    def complete_json(self, system: str, user: str, *, temperature: float = 0.2) -> dict:
        try:
            text = self.complete(system, user, json_mode=True, temperature=temperature)
        except LLMError as exc:
            # Groq валидирует JSON строго (json_validate_failed) — пробуем без response_format
            if "json_validate_failed" not in str(exc) and "Failed to validate JSON" not in str(exc):
                raise
            logger.info("Groq: строгий JSON-режим не принял ответ, повторяю без response_format")
            text = self.complete(system, user, json_mode=False, temperature=temperature)
        return parse_json_object(text)


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
