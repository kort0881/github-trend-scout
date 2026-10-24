from __future__ import annotations

import logging
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

from .analysis import analyze_all
from .archive import ARCHIVE_NAME, Archive
from .config import Config, ConfigError, load_config
from .ingestion import ingest
from .llm import GroqLLM
from .models import RepoRaw, ScoredRepo
from .prefilter import prefilter
from .publish import publish
from .scoring import rank
from .script_gen import generate_script
from .security import scan_all
from .storage import Storage

logger = logging.getLogger("scout")

SECURITY_WORKERS = int(os.getenv("SECURITY_WORKERS", "4"))


class PipelineError(RuntimeError):
    pass


@dataclass
class RunStats:
    ingested: int = 0
    prefiltred: int = 0
    fresh: int = 0
    scanned: int = 0
    analyzed: int = 0
    published: int = 0
    script_source: str = ""
    release: str = ""
    warnings: list[str] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            "──── сводка выпуска ────",
            f"собрано кандидатов:      {self.ingested}",
            f"после pre-filter:        {self.prefiltred}",
            f"новых (нет в state.db):  {self.fresh}",
            f"просканировано security: {self.scanned}",
            f"проанализировано LLM:    {self.analyzed}",
            f"опубликовано:            {self.published}",
        ]
        if self.script_source:
            lines.append(f"источник сценария:       {self.script_source}")
        if self.release:
            lines.append(f"директория выпуска:      {self.release}")
        return "\n".join(lines)


def setup_logging(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s"))
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)


def run_pipeline(
    config: Config,
    storage: Storage | None = None,
    llm: GroqLLM | None = None,
    client=None,
    archive: Archive | None = None,
) -> RunStats:
    stats = RunStats()
    storage = storage or Storage(config.data_dir)
    llm = llm or GroqLLM(config.groq_api_key, config.groq_model, config.groq_fallbacks)
    if archive is None:
        archive = Archive(config.output_dir / ARCHIVE_NAME)

    # 1. Ingestion — критичный этап
    try:
        raw_repos = ingest(config, client=client)
    except Exception as exc:  # noqa: BLE001
        raise PipelineError(f"Ingestion упал: {exc}") from exc
    stats.ingested = len(raw_repos)
    if not raw_repos:
        raise PipelineError("Ingestion вернул 0 репозиториев — публиковать нечего")

    # 2. Pre-filter
    try:
        filtered = prefilter(raw_repos, config)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Prefilter упал (%s), работаю с полным списком", exc)
        filtered = raw_repos
    stats.prefiltred = len(filtered)

    # state.db: не анализировать повторно
    try:
        fresh = storage.filter_new(filtered)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Storage недоступен (%s), продолжаю без дедупликации", exc)
        fresh = filtered

    # архив: репозиторий, однажды вышедший в выпуске, больше не повторяется
    if archive is not None:
        fresh = archive.exclude(fresh)
    stats.fresh = len(fresh)
    if not fresh:
        logger.info("Новых репозиториев нет: все кандидаты уже выходили или обработаны недавно — выпуск не нужен")
        return stats

    # 3. Security (некритичный, параллельно)
    try:
        security = scan_all(fresh, cache=storage, workers=SECURITY_WORKERS)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Security-этап упал целиком (%s), репозитории идут без отчётов", exc)
        security = {}
    stats.scanned = len(security)

    # 4. LLM-анализ (некритичный)
    try:
        analyses = analyze_all([(raw, security.get(raw.full_name)) for raw in fresh], config, llm=llm)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Analysis упал целиком (%s)", exc)
        analyses = {}
    stats.analyzed = len(analyses)
    if not analyses:
        raise PipelineError("Ни один репозиторий не прошёл LLM-анализ")

    # 5. Скоринг
    try:
        top = rank(fresh, analyses, security, config)
    except Exception as exc:  # noqa: BLE001
        raise PipelineError(f"Scoring упал: {exc}") from exc
    if not top:
        logger.warning("Scoring не дал ни одного репозитория — выпуск не публикуется")
        return stats

    # 6. Сценарий
    script, source = generate_script(top, config.prompts_dir, llm=llm)
    stats.script_source = "Groq" if source == "llm" else "шаблон (fallback)"

    # 7. Публикация — критичный этап
    try:
        release = publish(top, script, config.output_dir, root_readme=config.root / "README.md")
    except Exception as exc:  # noqa: BLE001
        raise PipelineError(f"Publish упал: {exc}") from exc
    stats.published = len(top)
    stats.release = str(release)

    for item in top:
        try:
            storage.mark_processed(item.raw.full_name, item.final_score)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Не удалось записать %s в state.db: %s", item.raw.full_name, exc)
    return stats


def main() -> int:
    setup_logging()
    try:
        config = load_config()
    except ConfigError as exc:
        logger.error("%s", exc)
        return 1
    try:
        stats = run_pipeline(config)
    except PipelineError as exc:
        logger.error("Пайплайн остановлен: %s", exc)
        return 1
    print(stats.summary())
    return 0


if __name__ == "__main__":
    sys.exit(main())
