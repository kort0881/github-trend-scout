from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from .llm import LLMError, GroqLLM
from .models import ScoredRepo

logger = logging.getLogger(__name__)

ORDINALS = [
    "Первый наш участник",
    "Номер два",
    "Третий участник",
    "Номер четыре",
    "Пятый участник",
    "Номер шесть",
    "Седьмой участник",
    "Номер восемь",
    "Девятый участник",
    "Номер десять",
]
MIN_WORDS, MAX_WORDS = 800, 1500


def _words(text: str) -> int:
    return len(re.findall(r"[\w\-]+", text, flags=re.UNICODE))


def _ordinal(index: int) -> str:
    return ORDINALS[index] if index < len(ORDINALS) else f"Номер {index + 1}"


def validate_script(text: str, repos: list[ScoredRepo]) -> list[str]:
    problems: list[str] = []
    if not text or not text.strip():
        return ["пустой сценарий"]
    for item in repos:
        if item.raw.full_name not in text:
            problems.append(f"нет упоминания {item.raw.full_name}")
        if item.raw.html_url not in text:
            problems.append(f"нет ссылки {item.raw.html_url}")
    words = _words(text)
    if words < MIN_WORDS:
        problems.append(f"объём {words} слов < {MIN_WORDS}")
    if words > MAX_WORDS:
        problems.append(f"объём {words} слов > {MAX_WORDS}")
    if "Ссылки" not in text:
        problems.append("нет раздела «Ссылки»")
    return problems


def fallback_script(repos: list[ScoredRepo]) -> str:
    """Детерминированная сборка по шаблону: гарантирует все N репо и все ссылки."""
    n = len(repos)
    parts: list[str] = [
        f"Всем привет! Сегодня у нас обзор {n} новых репозиториев, которые могут пригодиться абсолютно разным людям.",
    ]
    for index, item in enumerate(repos):
        raw, analysis, security = item.raw, item.analysis, item.security
        pros = "; ".join(analysis.pros) if analysis.pros else "понятная задача без лишних зависимостей"
        cons = "; ".join(analysis.cons) if analysis.cons else "проект молодой, документация ещё тонкая"
        audience = ", ".join(analysis.audience) if analysis.audience else "разработчики"
        parts.append(
            f"{_ordinal(index)} — {raw.full_name}.\n"
            f"Чем он примечателен: {analysis.summary}\n"
            f"Кому пригодится: {analysis.usefulness}\n"
            f"У него {pros}.\n"
            f"Но есть и недостатки: {cons}.\n"
            f"Чем отличается от аналогов: {analysis.uniqueness}\n"
            f"Целевая аудитория: {audience}. "
            f"На момент обзора у проекта {raw.stars} звёзд, {raw.forks} форков, "
            f"основной язык — {raw.language or 'не указан'}, лицензия — {raw.license or 'не указана'}. "
            f"Последний коммит: {raw.pushed_at.date().isoformat()}.\n"
            f"Проверка безопасности: {security.details}."
        )
    parts.append(
        "И в конце — все ссылки на репозитории в описании к видео.\n"
        "Спасибо за просмотр, подписывайтесь, чтобы не пропустить следующий выпуск!"
    )
    links = "\n".join(f"{i}. {item.raw.full_name} — {item.raw.html_url}" for i, item in enumerate(repos, start=1))
    parts.append(f"---\n\n## Ссылки\n{links}")
    return "\n\n".join(parts)


def _payload(repos: list[ScoredRepo]) -> str:
    data = [
        {
            "full_name": item.raw.full_name,
            "html_url": item.raw.html_url,
            "stars": item.raw.stars,
            "forks": item.raw.forks,
            "language": item.raw.language,
            "license": item.raw.license,
            "created_at": item.raw.created_at.date().isoformat(),
            "pushed_at": item.raw.pushed_at.date().isoformat(),
            "summary": item.analysis.summary,
            "usefulness": item.analysis.usefulness,
            "uniqueness": item.analysis.uniqueness,
            "pros": item.analysis.pros,
            "cons": item.analysis.cons,
            "audience": item.analysis.audience,
            "score": item.analysis.score,
            "security": item.security.details,
            "final_score": item.final_score,
        }
        for item in repos
    ]
    return json.dumps(data, ensure_ascii=False, indent=1)


def generate_script(repos: list[ScoredRepo], prompts_dir: Path, llm: GroqLLM | None = None) -> tuple[str, str]:
    """Возвращает (markdown, источник: 'llm' | 'fallback')."""
    if not repos:
        return "Выпуск пуст: подходящих репозиториев не нашлось.\n", "fallback"

    prompts_dir = Path(prompts_dir)
    system = (prompts_dir / "script_system.txt").read_text(encoding="utf-8")
    user = (prompts_dir / "script_user.txt").read_text(encoding="utf-8")
    user = user.replace("{{REPOS_JSON}}", _payload(repos)).replace("{{N}}", str(len(repos)))

    if llm is not None:
        try:
            text = llm.complete(system, user, temperature=0.6, max_tokens=8000)
            text = text.strip()
            if text.startswith("```"):
                blocks = text.split("```")
                text = blocks[1] if len(blocks) >= 2 else text.strip("`")
                if text.lstrip().lower().startswith("markdown"):
                    text = text.lstrip()[8:]
            problems = validate_script(text, repos)
            if not problems:
                logger.info("Script: сценарий от LLM прошёл валидацию (%s слов)", _words(text))
                return text.strip() + "\n", "llm"
            logger.warning("Script: LLM-сценарий не прошёл валидацию: %s", "; ".join(problems))
        except LLMError as exc:
            logger.warning("Script: LLM недоступен (%s), собираю по шаблону детерминированно", exc)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Script: сбой генерации (%s), перехожу на шаблон", exc)

    text = fallback_script(repos)
    problems = validate_script(text, repos)
    if problems:
        logger.warning("Script: шаблонная сборка неполна: %s", "; ".join(problems))
    return text + "\n", "fallback"
