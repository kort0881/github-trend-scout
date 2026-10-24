from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path

from .models import RepoRaw, ScoredRepo

logger = logging.getLogger(__name__)

LAST_RELEASE_START = "<!-- LAST_RELEASE:START -->"
LAST_RELEASE_END = "<!-- LAST_RELEASE:END -->"
TABLE_HEADER = "| Дата | Кол-во репо | Сценарий |\n|---|---|---|"
ROW_RE = re.compile(r"^\|\s*(\d{4}-\d{2}-\d{2})\s*\|")


def release_date(now: datetime | None = None) -> str:
    return (now or datetime.now(timezone.utc)).astimezone(timezone.utc).date().isoformat()


def _write_release_dir(output_dir: Path, date_str: str, script: str, repos: list[ScoredRepo]) -> Path:
    release = output_dir / date_str
    release.mkdir(parents=True, exist_ok=True)
    (release / "script.md").write_text(script, encoding="utf-8")
    raws: list[RepoRaw] = [item.raw for item in repos]
    (release / "repos.json").write_text(
        json.dumps([raw.model_dump(mode="json") for raw in raws], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (release / "analysis.json").write_text(
        json.dumps(
            [ScoredRepo.model_validate(item).model_dump(mode="json") for item in repos],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    logger.info("Publish: файлы выпуска записаны в %s", release)
    return release


def rebuild_index(output_dir: Path) -> Path:
    """Таблица-индекс выпусков в output/README.md, собранная из содержимого output/."""
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[str] = []
    for entry in sorted(output_dir.iterdir(), reverse=True):
        if not entry.is_dir() or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", entry.name):
            continue
        if not (entry / "script.md").exists():
            continue
        count = 0
        repos_file = entry / "repos.json"
        if repos_file.exists():
            try:
                count = len(json.loads(repos_file.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                count = 0
        rows.append(f"| {entry.name} | {count} | [script.md]({entry.name}/script.md) |")

    content = "# Выпуски\n\nАвтоматический индекс. Формируется пайплайном.\n\n" + TABLE_HEADER + "\n"
    content += ("\n".join(rows) if rows else "| — | 0 | — |") + "\n"
    index_path = output_dir / "README.md"
    index_path.write_text(content, encoding="utf-8")
    logger.info("Publish: индекс обновлён (%s выпусков)", len(rows))
    return index_path


def update_root_readme(readme_path: Path, date_str: str, count: int, output_dir: Path) -> bool:
    readme_path = Path(readme_path)
    if not readme_path.exists():
        logger.warning("Publish: %s не найден, блок последнего выпуска не обновлён", readme_path)
        return False
    text = readme_path.read_text(encoding="utf-8")
    try:
        rel_link = (output_dir / date_str / "script.md").relative_to(readme_path.parent).as_posix()
    except ValueError:
        rel_link = f"output/{date_str}/script.md"
    block = (
        f"{LAST_RELEASE_START}\n"
        f"**Последний выпуск:** {date_str} — {count} репозиториев — "
        f"[сценарий]({rel_link}) · [все выпуски]({rel_link.split('/')[0]}/README.md)\n"
        f"{LAST_RELEASE_END}"
    )
    if LAST_RELEASE_START in text and LAST_RELEASE_END in text:
        updated = re.sub(
            re.escape(LAST_RELEASE_START) + r".*?" + re.escape(LAST_RELEASE_END),
            block,
            text,
            flags=re.DOTALL,
        )
    else:
        updated = text.rstrip() + "\n\n" + block + "\n"
    readme_path.write_text(updated, encoding="utf-8")
    logger.info("Publish: корневой README обновлён (последний выпуск %s)", date_str)
    return True


def publish(
    repos: list[ScoredRepo],
    script: str,
    output_dir: Path,
    root_readme: Path | None = None,
    now: datetime | None = None,
) -> Path:
    date_str = release_date(now)
    release = _write_release_dir(Path(output_dir), date_str, script, repos)
    rebuild_index(Path(output_dir))
    if root_readme is not None:
        update_root_readme(Path(root_readme), date_str, len(repos), Path(output_dir))
    return release
