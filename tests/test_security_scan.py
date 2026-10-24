from __future__ import annotations

import src.security as security_module
from src.models import SecurityReport


def test_scan_all_parallel_collects_reports(make_repo, monkeypatch):
    calls: list[str] = []

    def fake_scan(repo, cache=None):
        calls.append(repo.full_name)
        return SecurityReport(details=f"ok {repo.full_name}")

    monkeypatch.setattr(security_module, "security_scan", fake_scan)
    repos = [make_repo(f"owner/repo{i}") for i in range(5)]
    result = security_module.scan_all(repos, cache=None, workers=3)

    assert sorted(result) == sorted(repo.full_name for repo in repos)
    assert len(calls) == 5
    assert all(report.passed for report in result.values())


def test_scan_all_survives_single_failure(make_repo, monkeypatch):
    def flaky_scan(repo, cache=None):
        if repo.full_name == "owner/broken":
            raise RuntimeError("scanner blew up")
        return SecurityReport(details="ok")

    monkeypatch.setattr(security_module, "security_scan", flaky_scan)
    repos = [make_repo("owner/ok"), make_repo("owner/broken")]
    result = security_module.scan_all(repos, workers=2)

    assert list(result) == ["owner/ok"]


def test_scan_all_empty_input():
    assert security_module.scan_all([], workers=2) == {}


def test_clone_is_defined():
    assert callable(security_module._clone)
