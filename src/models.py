from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class RepoRaw(BaseModel):
    full_name: str
    html_url: str
    description: str | None = None
    stars: int = 0
    forks: int = 0
    language: str | None = None
    license: str | None = None
    created_at: datetime
    pushed_at: datetime
    topics: list[str] = Field(default_factory=list)
    readme_excerpt: str | None = None
    archived: bool = False


class SecurityReport(BaseModel):
    semgrep_findings: int = 0
    bandit_findings: int = 0
    gitleaks_findings: int = 0
    critical_count: int = 0
    high_count: int = 0
    passed: bool = True
    details: str = ""


class RepoAnalysis(BaseModel):
    full_name: str
    summary: str
    usefulness: str
    uniqueness: str
    pros: list[str]
    cons: list[str]
    audience: list[str]
    score: float = Field(ge=0, le=10)


class ScoredRepo(BaseModel):
    raw: RepoRaw
    security: SecurityReport
    analysis: RepoAnalysis
    final_score: float
