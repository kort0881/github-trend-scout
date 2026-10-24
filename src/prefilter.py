from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from .config import Config
from .models import RepoRaw

logger = logging.getLogger(__name__)

ACTIVITY_WINDOW_DAYS = 30


def _aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def keep(repo: RepoRaw, min_stars: int = 100, now: datetime | None = None) -> bool:
    now = now or datetime.now(timezone.utc)
    if repo.stars < min_stars:
        return False
    if not repo.license:
        return False
    if _aware(repo.pushed_at) < now - timedelta(days=ACTIVITY_WINDOW_DAYS):
        return False
    if not (repo.description or "").strip():
        return False
    if repo.archived:
        return False
    return True


def prefilter(repos: list[RepoRaw], config: Config, now: datetime | None = None) -> list[RepoRaw]:
    kept = [r for r in repos if keep(r, config.min_stars, now)]
    logger.info("Prefilter: %s -> %s", len(repos), len(kept))
    if len(kept) < 15:
        logger.warning("Prefilter: после отсева меньше 15 репозиториев (%s), продолжаю с тем, что есть", len(kept))
    return kept
