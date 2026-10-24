from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from .models import ScoredRepo

logger = logging.getLogger(__name__)

ARCHIVE_NAME = "archive.json"


class Archive:
    """Постоянный список уже выходивших репозиториев (output/archive.json, коммитится в репо).

    SQLite в data/ живёт локально или в кэше CI, поэтому «не повторяться» гарантирует
    только файл внутри репозитория: он обновляется вместе с выпуском и переезжает
    между прогонами вместе с git.
    """

    def __init__(self, path: Path):
        self.path = Path(path)
        self.repos: dict[str, dict] = self._load()

    def _load(self) -> dict[str, dict]:
        if not self.path.exists():
            return {}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Archive: %s не прочитан (%s), считаю пустым", self.path, exc)
            return {}
        if isinstance(data, dict):
            items = data.get("repos", data)
        elif isinstance(data, list):
            items = {str(name): {} for name in data}
        else:
            items = {}
        return {str(k): (v if isinstance(v, dict) else {}) for k, v in items.items()}

    def __len__(self) -> int:
        return len(self.repos)

    def contains(self, full_name: str) -> bool:
        return full_name in self.repos

    def exclude(self, repos: list) -> list:
        """Убирает репозитории, которые уже были в прошлых выпусках."""
        fresh = [repo for repo in repos if not self.contains(repo.full_name)]
        skipped = len(repos) - len(fresh)
        if skipped:
            logger.info("Archive: %s уже выходивших репозиториев исключено", skipped)
        return fresh

    def add_release(self, release_date: str, items: list[ScoredRepo]) -> None:
        for item in items:
            name = item.raw.full_name
            entry = self.repos.get(name) or {"releases": [], "times": 0}
            releases = list(entry.get("releases") or [])
            is_new_release = release_date not in releases
            if is_new_release:
                releases.append(release_date)
            entry.update(
                {
                    "releases": releases,
                    "times": int(entry.get("times", 0)) + (1 if is_new_release else 0),
                    "last": release_date,
                    "score": item.final_score,
                    "html_url": item.raw.html_url,
                }
            )
            self.repos[name] = entry

    def save(self) -> None:
        payload = {
            "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "count": len(self.repos),
            "repos": dict(sorted(self.repos.items())),
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            logger.info("Archive: %s репозиториев в архиве (%s)", len(self.repos), self.path)
        except OSError as exc:
            logger.warning("Archive: не удалось записать %s (%s)", self.path, exc)
