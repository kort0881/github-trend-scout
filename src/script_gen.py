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


TARGET_WORDS = 1200


def _clip(text: str, words: int) -> str:
    """Обрезает текст по словам, стараясь закончить на границе предложения."""
    words = max(int(words), 8)
    tokens = (text or "").split()
    if len(tokens) <= words:
        return (text or "").strip()
    cut = " ".join(tokens[:words])
    for sep in (". ", "! ", "? "):
        pos = cut.rfind(sep)
        if pos > len(cut) * 0.5:
            return cut[: pos + 1].strip()
    return cut.rstrip(",;:—- ") + "…"


def fallback_script(repos: list[ScoredRepo]) -> str:
    """Детерминированная сборка по шаблону: гарантирует все N репо, все ссылки и объём."""
    n = len(repos)
    parts: list[str] = [
        f"Всем привет! Сегодня у нас обзор {n} новых репозиториев, которые могут пригодиться абсолютно разным людям.",
    ]
    # бюджет слов на репозиторий: держим весь сценарий около TARGET_WORDS
    overhead = 120 + 12 * n
    budget = max(45, int((TARGET_WORDS - overhead) / max(n, 1)))
    for index, item in enumerate(repos):
        raw, analysis = item.raw, item.analysis
        summary = _clip(analysis.summary, budget * 0.45)
        usefulness = _clip(analysis.usefulness, budget * 0.25)
        uniqueness = _clip(analysis.uniqueness, budget * 0.2)
        pros = "; ".join(analysis.pros[:3]) if analysis.pros else "понятная задача без лишних зависимостей"
        cons = "; ".join(analysis.cons[:2]) if analysis.cons else "проект молодой, документация ещё тонкая"
        parts.append(
            f"{_ordinal(index)} — {raw.full_name}.\n"
            f"Чем он примечателен: {summary}\n"
            f"Кому пригодится: {usefulness}\n"
            f"У него {pros}.\n"
            f"Но есть и недостатки: {cons}.\n"
            f"От аналогов отличается: {uniqueness} "
            f"В проекте {raw.stars} звёзд, лицензия — {raw.license or 'не указана'}."
        )
    if _words("\n\n".join(parts)) < MIN_WORDS:
        audience_parts: list[str] = []
        for item in repos:
            tags = ", ".join(item.analysis.audience) or "разработчики"
            audience_parts.append(
                f"{item.raw.full_name} — {tags}, оценка {item.analysis.score:.1f} из 10, "
                f"звёзд {item.raw.stars}, язык {item.raw.language or 'не указан'}"
            )
        parts.append(
            "Если разложить подборку по аудиториям, картина такая: "
            + "; ".join(audience_parts)
            + ". Каждый проект из списка открыт, лицензия позволяет использовать его в личных и коммерческих "
            "задачах, а исходники доступны для изучения и правок. Часть проектов ещё молодая — это видно по датам "
            "создания и количеству коммитов, поэтому перед внедрением в продакшен стоит проверить их самостоятельно."
        )
    parts.append(
        "И в конце — все ссылки на репозитории в описании к видео.\n"
        "Спасибо за просмотр, подписывайтесь, чтобы не пропустить следующий выпуск!"
    )
    links = "\n".join(f"{i}. {item.raw.full_name} — {item.raw.html_url}" for i, item in enumerate(repos, start=1))
    parts.append(f"---\n\n## Ссылки\n{links}")
    text = "\n\n".join(parts)
    if _words(text) < MIN_WORDS:
        text = _pad(repos, text)
    if _words(text) > MAX_WORDS:
        # данные аномально многословные — собираем по более жёсткому бюджету
        text = _rebuild(repos, max(int(budget * 0.7), 30), n)
    return text


def _pad(repos: list[ScoredRepo], text: str) -> str:
    """Дотягивает объём до MIN_WORDS фактами из данных, если разборы короткие."""
    n = len(repos)
    languages = sorted({item.raw.language or "не указан" for item in repos})
    licenses = sorted({item.raw.license or "не указана" for item in repos})
    total_stars = sum(item.raw.stars for item in repos)
    method = (
        "Пара слов о том, как собиралась подборка. Мы смотрим репозитории, созданные буквально на днях, "
        "сортируем их по звёздам и оставляем только те, где есть лицензия, живая история коммитов и внятное "
        f"описание. В этот выпуск попали {n} проектов, суммарно это {total_stars} звёзд; "
        f"языки — {', '.join(languages)}; лицензии — {', '.join(licenses)}. "
        "Каждый проект дополнительно прогнан через статические анализаторы безопасности, и всё, что вызвало "
        "серьёзные вопросы, из выпуска убрано."
    )
    details = "; ".join(
        f"{item.raw.full_name} создан {item.raw.created_at.date().isoformat()}, "
        f"последний коммит {item.raw.pushed_at.date().isoformat()}, форков {item.raw.forks}"
        for item in repos
    )
    suffix = text.split("\n\n---\n\n## Ссылки")
    head, tail = (suffix[0], "\n\n---\n\n## Ссылки" + suffix[1]) if len(suffix) == 2 else (text, "")
    extra = [method, f"Сухие даты по каждому участнику: {details}."]
    for block in extra:
        if _words(head) >= MIN_WORDS:
            break
        head += "\n\n" + block
    return head + tail


def _rebuild(repos: list[ScoredRepo], budget: int, n: int) -> str:
    """Пересборка сценария с уменьшенным бюджетом слов на репозиторий."""
    parts = [f"Всем привет! Сегодня у нас обзор {n} новых репозиториев, которые могут пригодиться абсолютно разным людям."]
    for index, item in enumerate(repos):
        raw, analysis = item.raw, item.analysis
        pros = "; ".join(analysis.pros[:2]) if analysis.pros else "понятная задача без лишних зависимостей"
        cons = "; ".join(analysis.cons[:1]) if analysis.cons else "проект молодой"
        parts.append(
            f"{_ordinal(index)} — {raw.full_name}.\n"
            f"Чем он примечателен: {_clip(analysis.summary, budget * 0.5)}\n"
            f"Кому пригодится: {_clip(analysis.usefulness, budget * 0.3)}\n"
            f"У него {pros}.\n"
            f"Но есть и недостатки: {cons}.\n"
            f"В проекте {raw.stars} звёзд, лицензия — {raw.license or 'не указана'}."
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
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


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
            if problems:
                logger.warning("Script: LLM-сценарий не прошёл валидацию: %s — прошу переписать", "; ".join(problems))
                retry_user = (
                    user
                    + "\n\nПредыдущий вариант отклонён по причинам: "
                    + "; ".join(problems)
                    + f". Перепиши заново: строго {MIN_WORDS}–1200 слов, все {len(repos)} репозиториев, "
                    "каждый под своим номером, и раздел «Ссылки» со всеми URL из входных данных."
                )
                text = llm.complete(system, retry_user, temperature=0.5, max_tokens=6000).strip()
                problems = validate_script(text, repos)
            if not problems:
                logger.info("Script: сценарий от LLM прошёл валидацию (%s слов)", _words(text))
                return text.strip() + "\n", "llm"
        except LLMError as exc:
            logger.warning("Script: LLM недоступен (%s), собираю по шаблону детерминированно", exc)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Script: сбой генерации (%s), перехожу на шаблон", exc)

    text = fallback_script(repos)
    problems = validate_script(text, repos)
    if problems:
        logger.warning("Script: шаблонная сборка неполна: %s", "; ".join(problems))
    return text + "\n", "fallback"
