from __future__ import annotations

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from pydantic import ValidationError

from .config import Config
from .llm import LLMError, GroqLLM
from .models import RepoAnalysis, RepoRaw, SecurityReport

logger = logging.getLogger(__name__)

MAX_WORKERS = 1
PROMPT_README_CHARS = 2000
REQUEST_STAGGER = 8.0


def _read_prompt(prompts_dir: Path, name: str) -> str:
    return (Path(prompts_dir) / name).read_text(encoding="utf-8")


def repo_block(raw: RepoRaw, security: SecurityReport | None = None) -> str:
    lines = [
        f"full_name: {raw.full_name}",
        f"html_url: {raw.html_url}",
        f"описание: {raw.description or 'нет'}",
        f"язык: {raw.language or 'не указан'}",
        f"звёзд: {raw.stars}",
        f"форков: {raw.forks}",
        f"лицензия: {raw.license or 'нет'}",
        f"создан: {raw.created_at.date().isoformat()}",
        f"последний пуш: {raw.pushed_at.date().isoformat()}",
        f"темы: {', '.join(raw.topics) if raw.topics else 'нет'}",
    ]
    if security is not None:
        lines.append(f"безопасность: {security.details}")
    lines.append("README (фрагмент):")
    lines.append((raw.readme_excerpt or "(README недоступен)")[:PROMPT_README_CHARS])
    return "\n".join(lines)


def build_analysis_prompt(raw: RepoRaw, security: SecurityReport | None, prompts_dir: Path) -> tuple[str, str]:
    system = _read_prompt(prompts_dir, "analysis_system.txt")
    template = _read_prompt(prompts_dir, "analysis_user.txt")
    return system, template.replace("{{REPO_BLOCK}}", repo_block(raw, security))


def analyze_repo(
    raw: RepoRaw,
    security: SecurityReport | None,
    llm: GroqLLM,
    prompts_dir: Path,
) -> RepoAnalysis | None:
    system, user = build_analysis_prompt(raw, security, prompts_dir)
    for attempt in (1, 2):
        prompt = user
        if attempt == 2:
            prompt += (
                "\n\nПредыдущий ответ не прошёл валидацию JSON. Верни ТОЛЬКО валидный JSON-объект "
                "строго по схеме: full_name, summary, usefulness, uniqueness, pros, cons, audience, score."
            )
        try:
            data = llm.complete_json(system, prompt)
            data["full_name"] = data.get("full_name") or raw.full_name
            analysis = RepoAnalysis.model_validate(data)
            # модель не должна подменять репозиторий
            if analysis.full_name != raw.full_name:
                analysis = analysis.model_copy(update={"full_name": raw.full_name})
            return analysis
        except (LLMError, ValueError, ValidationError) as exc:
            logger.warning("Analysis: %s, попытка %s/2 не удалась (%s)", raw.full_name, attempt, exc)
    logger.warning("Analysis: %s исключён из выпуска", raw.full_name)
    return None


def analyze_all(
    items: list[tuple[RepoRaw, SecurityReport | None]],
    config: Config,
    llm: GroqLLM | None = None,
) -> dict[str, RepoAnalysis]:
    if not items:
        return {}
    llm = llm or GroqLLM(config.groq_api_key, config.groq_model, config.groq_fallbacks)
    results: dict[str, RepoAnalysis] = {}

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {}
        for index, (raw, security) in enumerate(items):
            if index:
                time.sleep(REQUEST_STAGGER)  # ровный темп, без всплесков в лимит Groq
            futures[pool.submit(analyze_repo, raw, security, llm, config.prompts_dir)] = raw.full_name
        for future in as_completed(futures):
            name = futures[future]
            try:
                analysis = future.result()
            except Exception as exc:  # noqa: BLE001
                logger.warning("Analysis: %s упал с ошибкой %s", name, exc)
                continue
            if analysis is not None:
                results[name] = analysis
                logger.info("Analysis: %s -> score %.1f", name, analysis.score)

    logger.info("Analysis: разобрано %s из %s", len(results), len(items))
    return results
