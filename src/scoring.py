from __future__ import annotations

import logging
import math
from datetime import datetime, timedelta, timezone

from .config import Config
from .models import RepoAnalysis, RepoRaw, ScoredRepo, SecurityReport

logger = logging.getLogger(__name__)

MIN_ANALYSIS_SCORE = 3.0


def _aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def normalized_stars(stars: int) -> float:
    return min(math.log10(stars + 1) / 5, 1.0)


def recency_bonus(created_at: datetime, now: datetime | None = None) -> float:
    now = now or datetime.now(timezone.utc)
    age_days = (now - _aware(created_at)).total_seconds() / 86400
    if age_days <= 7:
        return 1.0
    if age_days >= 30:
        return 0.0
    return 1.0 - (age_days - 7) / 23


def activity_bonus(pushed_at: datetime, now: datetime | None = None) -> float:
    now = now or datetime.now(timezone.utc)
    return 1.0 if _aware(pushed_at) >= now - timedelta(days=3) else 0.0


def final_score(
    raw: RepoRaw,
    analysis: RepoAnalysis,
    security: SecurityReport | None = None,
    now: datetime | None = None,
) -> float:
    security = security or SecurityReport()
    score = (
        0.40 * analysis.score
        + 0.25 * normalized_stars(raw.stars)
        + 0.15 * recency_bonus(raw.created_at, now)
        + 0.10 * (1.0 if security.passed else 0.0)
        + 0.10 * activity_bonus(raw.pushed_at, now)
    )
    return round(score, 3)


def rank(
    raw_repos: list[RepoRaw],
    analyses: dict[str, RepoAnalysis],
    security: dict[str, SecurityReport],
    config: Config,
    now: datetime | None = None,
) -> list[ScoredRepo]:
    scored: list[ScoredRepo] = []
    dropped_security = dropped_quality = 0

    for raw in raw_repos:
        analysis = analyses.get(raw.full_name)
        if analysis is None:
            continue
        report = security.get(raw.full_name) or SecurityReport()
        if report.critical_count > 0:
            dropped_security += 1
            logger.warning("Scoring: %s отсеян — critical-находки (%s)", raw.full_name, report.critical_count)
            continue
        if analysis.score < MIN_ANALYSIS_SCORE:
            dropped_quality += 1
            logger.info("Scoring: %s отсеян — низкая оценка %.1f", raw.full_name, analysis.score)
            continue
        scored.append(
            ScoredRepo(raw=raw, security=report, analysis=analysis, final_score=final_score(raw, analysis, report, now))
        )

    scored.sort(key=lambda item: item.final_score, reverse=True)
    top = scored[: config.max_repos]
    logger.info(
        "Scoring: к отбору %s, отсеяно по безопасности %s, по качеству %s, в выпуске %s",
        len(scored), dropped_security, dropped_quality, len(top),
    )
    if len(top) < 5:
        logger.warning("Scoring: в выпуске меньше 5 репозиториев (%s) — публикую что есть", len(top))
    return top
