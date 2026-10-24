from __future__ import annotations

from src.scoring import final_score, normalized_stars, rank


def test_normalized_stars_is_capped():
    assert normalized_stars(99999) == 1.0
    assert normalized_stars(999999) == 1.0
    assert normalized_stars(0) == 0.0
    assert round(normalized_stars(1000), 4) == 0.6001


def test_top_repo_score(make_repo, make_analysis, passed_security, now):
    raw = make_repo(stars=99999, created_days_ago=2, pushed_days_ago=1)
    assert final_score(raw, make_analysis(score=9.0), passed_security, now) == 4.2


def test_average_repo_score(make_repo, make_analysis, passed_security, now):
    raw = make_repo(stars=1000, created_days_ago=15, pushed_days_ago=10)
    failed = passed_security.model_copy(update={"passed": False, "high_count": 2})
    # 0.40*6 + 0.25*0.60008 + 0.15*0.65217 + 0 + 0
    assert final_score(raw, make_analysis(score=6.0), failed, now) == 2.648


def test_garbage_repo_score(make_repo, make_analysis, passed_security, now):
    raw = make_repo(stars=0, created_days_ago=60, pushed_days_ago=100)
    failed = passed_security.model_copy(update={"passed": False})
    assert final_score(raw, make_analysis(score=2.0), failed, now) == 0.8


def test_rank_sorts_and_limits(make_repo, make_analysis, passed_security, now):
    class Cfg:
        max_repos = 2

    raws = [
        make_repo("a/top", stars=99999, created_days_ago=1),
        make_repo("b/mid", stars=1000, created_days_ago=15),
        make_repo("c/low", stars=200, created_days_ago=20),
        make_repo("d/bad", stars=500, created_days_ago=3),
    ]
    analyses = {
        "a/top": make_analysis("a/top", 9.0),
        "b/mid": make_analysis("b/mid", 6.0),
        "c/low": make_analysis("c/low", 1.0),
        "d/bad": make_analysis("d/bad", 8.0),
    }
    security = {
        "a/top": passed_security,
        "b/mid": passed_security,
        "c/low": passed_security,
        "d/bad": passed_security.model_copy(update={"passed": False, "critical_count": 1}),
    }
    top = rank(raws, analyses, security, Cfg(), now=now)
    assert [item.raw.full_name for item in top] == ["a/top", "b/mid"]
    assert top[0].final_score > top[1].final_score


def test_rank_drops_critical_and_weak(make_repo, make_analysis, passed_security, now):
    class Cfg:
        max_repos = 10

    raws = [make_repo("a/weak"), make_repo("b/critical")]
    analyses = {"a/weak": make_analysis("a/weak", 2.5), "b/critical": make_analysis("b/critical", 9.0)}
    security = {
        "a/weak": passed_security,
        "b/critical": passed_security.model_copy(update={"passed": False, "critical_count": 2}),
    }
    assert rank(raws, analyses, security, Cfg(), now=now) == []
