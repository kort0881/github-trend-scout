from __future__ import annotations

import json

from src.storage import CACHE_VERSION, Storage


def test_cache_roundtrip(tmp_path):
    storage = Storage(tmp_path)
    storage.set_raw("owner/repo", {"passed": True, "details": "ok"})
    assert storage.get_raw("owner/repo")["details"] == "ok"


def test_stale_cache_version_is_ignored(tmp_path):
    storage = Storage(tmp_path)
    path = storage.cache_dir / "owner__repo.json"
    path.write_text(json.dumps({"cache_version": CACHE_VERSION - 1, "report": {"details": "старый разбор"}}), encoding="utf-8")
    assert storage.get_raw("owner/repo") is None
