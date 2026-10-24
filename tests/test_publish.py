from __future__ import annotations

import json
from datetime import datetime, timezone

from src.models import ScoredRepo
from src.publish import publish, rebuild_index, update_root_readme, LAST_RELEASE_START
from src.storage import Storage


def _scored(make_repo, make_analysis, passed_security, name: str, score: float = 8.0) -> ScoredRepo:
    return ScoredRepo(raw=make_repo(name), security=passed_security, analysis=make_analysis(name, score), final_score=score)


def test_publish_writes_three_files_and_index(tmp_path, make_repo, make_analysis, passed_security):
    repos = [_scored(make_repo, make_analysis, passed_security, "owner/repo1")]
    root_readme = tmp_path / "README.md"
    root_readme.write_text("# Проект\n\nТекст.\n", encoding="utf-8")
    release = publish(repos, "Всем привет! ...", tmp_path / "output", root_readme, now=datetime(2026, 10, 24, tzinfo=timezone.utc))

    assert release.name == "2026-10-24"
    assert (release / "script.md").exists()
    repos_json = json.loads((release / "repos.json").read_text(encoding="utf-8"))
    analysis_json = json.loads((release / "analysis.json").read_text(encoding="utf-8"))
    assert repos_json[0]["full_name"] == "owner/repo1"
    assert analysis_json[0]["security"]["passed"] is True

    index = (tmp_path / "output" / "README.md").read_text(encoding="utf-8")
    assert "| 2026-10-24 | 1 |" in index
    assert LAST_RELEASE_START in root_readme.read_text(encoding="utf-8")


def test_rebuild_index_skips_non_release_dirs(tmp_path):
    (tmp_path / "2026-10-01").mkdir()
    (tmp_path / "2026-10-01" / "script.md").write_text("x", encoding="utf-8")
    (tmp_path / "cache").mkdir()
    (tmp_path / "notes.md").write_text("x", encoding="utf-8")
    text = rebuild_index(tmp_path).read_text(encoding="utf-8")
    assert "2026-10-01" in text and "cache" not in text


def test_update_root_readme_is_idempotent(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("# Инит\n", encoding="utf-8")
    output = tmp_path / "output"
    update_root_readme(readme, "2026-10-24", 3, output)
    update_root_readme(readme, "2026-10-27", 5, output)
    text = readme.read_text(encoding="utf-8")
    assert text.count(LAST_RELEASE_START) == 1
    assert "2026-10-27" in text and "2026-10-24 | 3" not in text


def test_storage_dedup_and_cache(tmp_path, make_repo, now):
    storage = Storage(tmp_path)
    repo = make_repo("owner/repo1")
    assert storage.filter_new([repo], now=now) == [repo]
    storage.mark_processed(repo.full_name, 4.1, now=now)
    assert storage.filter_new([repo], now=now) == []
    assert storage.recently_processed(repo.full_name, now=now) is True

    storage.set_raw(repo.full_name, {"passed": True, "details": "ok"})
    assert storage.get_raw(repo.full_name)["details"] == "ok"
