from __future__ import annotations

import logging
from pathlib import Path

from .models import ScoredRepo

logger = logging.getLogger(__name__)

ORDINALS = [
    "Первый", "Второй", "Третий", "Четвёртый", "Пятый",
    "Шестой", "Седьмой", "Восьмой", "Девятый", "Десятый",
]


def _ordinal(index: int) -> str:
    return ORDINALS[index] if index < len(ORDINALS) else f"№{index + 1}"


def repo_review(index: int, item: ScoredRepo) -> str:
    """Обзор одного репозитория: что это, кому пригодится, плюсы и минусы."""
    raw, analysis, security = item.raw, item.analysis, item.security
    pros = "\n".join(f"- {p}" for p in (analysis.pros or ["—"]))
    cons = "\n".join(f"- {c}" for c in (analysis.cons or ["—"]))
    audience = ", ".join(analysis.audience) if analysis.audience else "разработчики"
    return (
        f"### {_ordinal(index)} — [{raw.full_name}]({raw.html_url})\n\n"
        f"{analysis.summary}\n\n"
        f"**Кому пригодится:** {analysis.usefulness} ({audience})\n\n"
        f"**Чем отличается от аналогов:** {analysis.uniqueness}\n\n"
        f"**Плюсы:**\n{pros}\n\n"
        f"**Минусы:**\n{cons}\n\n"
        f"**Метрики:** {raw.stars} звёзд · {raw.forks} форков · язык {raw.language or 'не указан'} · "
        f"лицензия {raw.license or 'не указана'} · создан {raw.created_at.date().isoformat()} · "
        f"последний коммит {raw.pushed_at.date().isoformat()}\n\n"
        f"**Проверка безопасности:** {security.details}\n\n"
        f"**Оценка:** {analysis.score:.1f}/10 · итоговый скор {item.final_score:.2f}\n"
    )


def generate_review(repos: list[ScoredRepo], output_dir: Path | None = None, date_str: str = "") -> str:
    """Markdown-обзор выпуска: без LLM и без сценария — только факты из анализа."""
    if not repos:
        return "Подходящих репозиториев не нашлось.\n"

    lines = [
        f"# Обзор {len(repos)} репозиториев{' — ' + date_str if date_str else ''}",
        "",
        "Подборка собрана автоматически: репозитории отобраны по звёздам и активности, "
        "проверены статическими анализаторами безопасности и разобраны моделью.",
        "",
        "## Содержание",
        "",
    ]
    lines += [f"{i}. [{item.raw.full_name}](#{i}-{item.raw.full_name.replace('/', '').lower()})" for i, item in enumerate(repos, start=1)]
    lines.append("")
    for index, item in enumerate(repos):
        lines.append(repo_review(index, item))
    lines.append("## Ссылки\n")
    lines += [f"{i}. {item.raw.full_name} — {item.raw.html_url}" for i, item in enumerate(repos, start=1)]
    return "\n".join(lines) + "\n"
