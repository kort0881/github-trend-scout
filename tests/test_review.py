from __future__ import annotations

from src.models import ScoredRepo
from src.review import generate_review


def _item(make_repo, make_analysis, passed_security, name):
    return ScoredRepo(raw=make_repo(name), security=passed_security, analysis=make_analysis(name), final_score=4.2)


def test_review_contains_all_repos_pros_cons_and_links(make_repo, make_analysis, passed_security):
    repos = [_item(make_repo, make_analysis, passed_security, f"owner/repo{i}") for i in range(3)]
    text = generate_review(repos, date_str="2026-10-24")
    for item in repos:
        assert item.raw.full_name in text
        assert item.raw.html_url in text
    assert text.count("**Плюсы:**") == 3
    assert text.count("**Минусы:**") == 3
    assert text.count("**Кому пригодится:**") == 3
    assert "## Ссылки" in text
    assert "Обзор 3 репозиториев" in text


def test_review_has_no_script_words(make_repo, make_analysis, passed_security):
    text = generate_review([_item(make_repo, make_analysis, passed_security, "owner/repo")])
    for marker in ("Спасибо за просмотр", "подписывайтесь", "Первый наш участник"):
        assert marker not in text


def test_empty_review():
    assert "не нашлось" in generate_review([])
