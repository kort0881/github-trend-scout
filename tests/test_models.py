from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.models import RepoAnalysis, RepoRaw, ScoredRepo, SecurityReport


def test_repo_raw_accepts_full_payload(make_repo):
    repo = make_repo()
    assert repo.full_name == "owner/repo"
    assert repo.stars == 1500
    assert repo.license == "MIT"


def test_repo_raw_rejects_broken_dates(make_repo):
    payload = make_repo().model_dump()
    payload["created_at"] = "не дата"
    with pytest.raises(ValidationError):
        RepoRaw.model_validate(payload)


def test_repo_analysis_score_bounds(make_analysis):
    with pytest.raises(ValidationError):
        RepoAnalysis(**{**make_analysis().model_dump(), "score": 11})
    with pytest.raises(ValidationError):
        RepoAnalysis(**{**make_analysis().model_dump(), "score": -1})


def test_repo_analysis_requires_all_fields(make_analysis):
    payload = make_analysis().model_dump()
    payload.pop("uniqueness")
    with pytest.raises(ValidationError):
        RepoAnalysis.model_validate(payload)


def test_scored_repo_roundtrip(make_repo, make_analysis, passed_security):
    scored = ScoredRepo(
        raw=make_repo(), security=passed_security, analysis=make_analysis(), final_score=3.4
    )
    dumped = scored.model_dump(mode="json")
    assert ScoredRepo.model_validate(dumped).final_score == 3.4


def test_security_report_defaults_are_passed():
    report = SecurityReport()
    assert report.passed is True
    assert report.critical_count == 0
