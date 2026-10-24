from __future__ import annotations

from src.models import ScoredRepo
from src.script_gen import _words, fallback_script, generate_script, validate_script


def _scored(make_repo, make_analysis, passed_security, name: str, score: float = 8.0) -> ScoredRepo:
    return ScoredRepo(
        raw=make_repo(name),
        security=passed_security,
        analysis=make_analysis(name, score),
        final_score=score,
    )


def test_fallback_contains_every_repo_and_link(make_repo, make_analysis, passed_security):
    repos = [_scored(make_repo, make_analysis, passed_security, f"owner/repo{i}") for i in range(10)]
    text = fallback_script(repos)
    for item in repos:
        assert item.raw.full_name in text
        assert item.raw.html_url in text
    assert "## Ссылки" in text
    assert "Всем привет!" in text
    assert "Спасибо за просмотр" in text
    assert _words(text) >= 800
    assert _words(text) <= 1500, f"шаблонный сценарий слишком длинный: {_words(text)} слов"


def test_validate_script_reports_missing_repo(make_repo, make_analysis, passed_security):
    repos = [_scored(make_repo, make_analysis, passed_security, "owner/repo1")]
    problems = validate_script("Всем привет! Спасибо за просмотр!", repos)
    assert any("owner/repo1" in problem for problem in problems)
    assert any("слов" in problem for problem in problems)


def test_generate_script_falls_back_on_bad_llm(make_repo, make_analysis, passed_security):
    class BadLLM:
        def complete(self, *args, **kwargs):
            return "короткая заглушка"

    repos = [_scored(make_repo, make_analysis, passed_security, "owner/repo1")]
    text, source = generate_script(repos, "prompts", llm=BadLLM())
    assert source == "fallback"
    assert "owner/repo1" in text and "https://github.com/owner/repo1" in text


def test_generate_script_uses_good_llm(make_repo, make_analysis, passed_security):
    repos = [_scored(make_repo, make_analysis, passed_security, f"owner/repo{i}") for i in range(10)]
    body = fallback_script(repos)

    class GoodLLM:
        def complete(self, *args, **kwargs):
            return body

    text, source = generate_script(repos, "prompts", llm=GoodLLM())
    assert source == "llm"
    assert text.strip() == body.strip()
