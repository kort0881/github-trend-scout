from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.models import RepoAnalysis, RepoRaw, SecurityReport  # noqa: E402

NOW = datetime(2026, 10, 24, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def now() -> datetime:
    return NOW


@pytest.fixture
def make_repo():
    def _make(
        full_name: str = "owner/repo",
        *,
        stars: int = 1500,
        forks: int = 120,
        license: str | None = "MIT",
        description: str | None = "Полезный инструмент",
        created_days_ago: int = 2,
        pushed_days_ago: int = 1,
        archived: bool = False,
        language: str | None = "Python",
        topics: list[str] | None = None,
        readme_excerpt: str | None = "README",
    ) -> RepoRaw:
        return RepoRaw(
            full_name=full_name,
            html_url=f"https://github.com/{full_name}",
            description=description,
            stars=stars,
            forks=forks,
            language=language,
            license=license,
            created_at=NOW - timedelta(days=created_days_ago),
            pushed_at=NOW - timedelta(days=pushed_days_ago),
            topics=topics or ["cli", "tooling"],
            readme_excerpt=readme_excerpt,
            archived=archived,
        )

    return _make


@pytest.fixture
def make_analysis():
    def _make(full_name: str = "owner/repo", score: float = 8.0) -> RepoAnalysis:
        return RepoAnalysis(
            full_name=full_name,
            summary="Проект делает X и решает Y.",
            usefulness="Пригодится бэкенд-разработчикам для быстрого старта.",
            uniqueness="Уникальная поддержка Z и минимальные зависимости.",
            pros=["быстрый", "минимальные зависимости"],
            cons=["мало документации"],
            audience=["backend", "devops"],
            score=score,
        )

    return _make


@pytest.fixture
def passed_security() -> SecurityReport:
    return SecurityReport(critical_count=0, high_count=0, passed=True, details="Находки — semgrep: 0, bandit: 0, gitleaks: 0; critical=0, high=0")
