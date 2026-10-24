from __future__ import annotations

from src.prefilter import keep, prefilter


def test_keeps_good_repo(make_repo, now):
    assert keep(make_repo(), min_stars=100, now=now) is True


def test_drops_low_stars(make_repo, now):
    assert keep(make_repo(stars=99), min_stars=100, now=now) is False


def test_drops_missing_license(make_repo, now):
    assert keep(make_repo(license=None), min_stars=100, now=now) is False


def test_drops_stale_repo(make_repo, now):
    assert keep(make_repo(pushed_days_ago=31), min_stars=100, now=now) is False


def test_drops_empty_description(make_repo, now):
    assert keep(make_repo(description="   "), min_stars=100, now=now) is False


def test_drops_archived(make_repo, now):
    assert keep(make_repo(archived=True), min_stars=100, now=now) is False


def test_prefilter_returns_subset(make_repo, now):
    class Cfg:
        min_stars = 100

    repos = [make_repo("a/one"), make_repo("b/two", stars=10), make_repo("c/three", license=None)]
    kept = prefilter(repos, Cfg(), now=now)
    assert [r.full_name for r in kept] == ["a/one"]
