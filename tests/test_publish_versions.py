from __future__ import annotations

from datetime import datetime, timezone

from src.models import ScoredRepo
from src.publish import publish, rebuild_index

NOW = datetime(2026, 10, 24, tzinfo=timezone.utc)


def _item(make_repo, make_analysis, passed_security, name: str, score: float = 8.0) -> ScoredRepo:
    return ScoredRepo(raw=make_repo(name), security=passed_security, analysis=make_analysis(name, score), final_score=score)


def test_second_release_same_day_gets_suffix(tmp_path, make_repo, make_analysis, passed_security):
    repos = [_item(make_repo, make_analysis, passed_security, "owner/repo1")]
    first = publish(repos, "раз", tmp_path / "output", now=NOW)
    second = publish(repos, "два", tmp_path / "output", now=NOW)
    third = publish(repos, "три", tmp_path / "output", now=NOW)

    assert first.name == "2026-10-24"
    assert second.name == "2026-10-24-2"
    assert third.name == "2026-10-24-3"
    assert (first / "script.md").read_text(encoding="utf-8") == "раз"


def test_index_lists_releases_with_suffix(tmp_path, make_repo, make_analysis, passed_security):
    repos = [_item(make_repo, make_analysis, passed_security, "owner/repo1")]
    publish(repos, "раз", tmp_path / "output", now=NOW)
    publish(repos, "два", tmp_path / "output", now=NOW)
    index = rebuild_index(tmp_path / "output").read_text(encoding="utf-8")
    assert "2026-10-24-2" in index and "| 2026-10-24 |" in index


def test_publish_keeps_previous_release_intact(tmp_path, make_repo, make_analysis, passed_security):
    run1 = [_item(make_repo, make_analysis, passed_security, "owner/first")]
    run2 = [_item(make_repo, make_analysis, passed_security, "owner/second")]
    publish(run1, "первый", tmp_path / "output", now=NOW)
    publish(run2, "второй", tmp_path / "output", now=NOW)

    assert (tmp_path / "output" / "2026-10-24" / "repos.json").exists()
    assert (tmp_path / "output" / "2026-10-24-2" / "repos.json").exists()
