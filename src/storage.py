from __future__ import annotations

import json
import logging
import sqlite3
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .models import RepoRaw

logger = logging.getLogger(__name__)

CACHE_TTL_SECONDS = 24 * 3600
# версия логики разбора сканеров: при её смене кэш отчётов игнорируется
CACHE_VERSION = 2


class Storage:
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.cache_dir = self.data_dir / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_dir / "state.db"
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS processed_repos (
                    full_name TEXT PRIMARY KEY,
                    first_seen TEXT NOT NULL,
                    last_analyzed TEXT NOT NULL,
                    final_score REAL
                )
                """
            )

    def recently_processed(self, full_name: str, days: int = 3, now: datetime | None = None) -> bool:
        now = now or datetime.now(timezone.utc)
        with self._connect() as conn:
            row = conn.execute(
                "SELECT last_analyzed FROM processed_repos WHERE full_name = ?", (full_name,)
            ).fetchone()
        if not row:
            return False
        try:
            last = datetime.fromisoformat(row["last_analyzed"])
        except ValueError:
            return False
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
        return last > now - timedelta(days=days)

    def mark_processed(self, full_name: str, final_score: float | None = None, now: datetime | None = None) -> None:
        now = now or datetime.now(timezone.utc)
        stamp = now.isoformat(timespec="seconds")
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO processed_repos (full_name, first_seen, last_analyzed, final_score)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(full_name) DO UPDATE SET
                    last_analyzed = excluded.last_analyzed,
                    final_score = excluded.final_score
                """,
                (full_name, stamp, stamp, final_score),
            )

    def filter_new(self, repos: list[RepoRaw], days: int = 3, now: datetime | None = None) -> list[RepoRaw]:
        fresh = [r for r in repos if not self.recently_processed(r.full_name, days, now)]
        logger.info("Storage: свежих репозиториев %s из %s (остальные обработаны < %s дней назад)", len(fresh), len(repos), days)
        return fresh

    # ---- JSON-кэш сырых ответов сканеров ----

    def _cache_file(self, full_name: str) -> Path:
        return self.cache_dir / f"{full_name.replace('/', '__')}.json"

    def get_raw(self, full_name: str) -> dict | None:
        path = self._cache_file(full_name)
        if not path.exists():
            return None
        if time.time() - path.stat().st_mtime > CACHE_TTL_SECONDS:
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        if data.get("cache_version") != CACHE_VERSION:
            logger.info("Кэш %s устарел (версия разбора изменилась) — пересканирую", full_name)
            return None
        report = data.get("report")
        return report if isinstance(report, dict) else None

    def set_raw(self, full_name: str, report: dict, raw: dict | None = None) -> None:
        path = self._cache_file(full_name)
        payload = {
            "cache_version": CACHE_VERSION,
            "report": report,
            "raw": raw or {},
            "saved_at": datetime.now(timezone.utc).isoformat(),
        }
        try:
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError as exc:
            logger.warning("Не удалось записать кэш для %s: %s", full_name, exc)
