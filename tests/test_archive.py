from __future__ import annotations

import json
from datetime import datetime, timezone

from src.archive import ARCHIVE_NAME, Archive
from src.models import ScoredRepo
from src.publish import publish


def _scored(make_repo, make_analysis, passed_security, name: str) -> ScoredRepo:
    return ScoredRepo(
        raw=make_repo(name), security=passed_security, analysis=make_analysis(name), final_score=3.5
    )


def test_archive_starts_empty(tmp_path):
    archive = Archive(tmp_path / ARCHIVE_NAME)
    assert len(archive) == 0
    assert archive.contains("owner/repo") is False


def test_add_release_survives_reload(tmp_path, make_repo, make_analysis, passed_security):
    path = tmp_path / ARCHIVE_NAME
    archive = Archive(path)
    archive.add_release("2026-10-24", [_scored(make_repo, make_analysis, passed_security, "owner/repo1")])
    archive.save()

    reloaded = Archive(path)
    assert reloaded.contains("owner/repo1")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["repos"]["owner/repo1"]["releases"] == ["2026-10-24"]
    assert payload["repos"]["owner/repo1"]["times"] == 1


def test_repeated_release_does_not_duplicate(tmp_path, make_repo, make_analysis, passed_security):
    archive = Archive(tmp_path / ARCHIVE_NAME)
    item = _scored(make_repo, make_analysis, passed_security, "owner/repo1")
    archive.add_release("2026-10-24", [item])
    archive.add_release("2026-10-24", [item])
    assert archive.repos["owner/repo1"]["releases"] == ["2026-10-24"]
    assert archive.repos["owner/repo1"]["times"] == 1


def test_exclude_drops_known_repos(tmp_path, make_repo):
    archive = Archive(tmp_path / ARCHIVE_NAME)
    archive.repos["known/repo"] = {"releases": ["2026-01-01"]}
    fresh = archive.exclude([make_repo("known/repo"), make_repo("new/repo")])
    assert [r.full_name for r in fresh] == ["new/repo"]


def test_corrupted_archive_is_treated_as_empty(tmp_path):
    path = tmp_path / ARCHIVE_NAME
    path.write_text("{не json", encoding="utf-8")
    assert len(Archive(path)) == 0


def test_publish_updates_archive(tmp_path, make_repo, make_analysis, passed_security):
    repos = [_scored(make_repo, make_analysis, passed_security, "owner/repo1")]
    publish(repos, "текст", tmp_path / "output", now=datetime(2026, 10, 24, tzinfo=timezone.utc))
    archive = Archive(tmp_path / "output" / ARCHIVE_NAME)
    assert archive.contains("owner/repo1")
