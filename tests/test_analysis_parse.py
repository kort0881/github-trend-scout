from __future__ import annotations

import json

import pytest

from src.analysis import analyze_repo, build_analysis_prompt, repo_block
from src.llm import GroqLLM, parse_json_object
from src.models import RepoAnalysis

GOOD_ANSWER = {
    "full_name": "owner/repo",
    "summary": "Инструмент для X. Работает из коробки.",
    "usefulness": "Бэкендерам для быстрого прототипа.",
    "uniqueness": "Аналогов с такой поддержкой Z мало.",
    "pros": ["быстро", "без зависимостей"],
    "cons": ["нет документации"],
    "audience": ["backend"],
    "score": 7.5,
}


class FakeLLM:
    def __init__(self, answers: list[str]):
        self.answers = answers
        self.calls = 0

    def complete_json(self, system: str, user: str, **kwargs) -> dict:
        self.calls += 1
        answer = self.answers[min(self.calls - 1, len(self.answers) - 1)]
        return parse_json_object(answer)


def test_parse_json_object_handles_code_fence():
    text = "```json\n" + json.dumps(GOOD_ANSWER) + "\n```"
    assert parse_json_object(text)["full_name"] == "owner/repo"


def test_parse_json_object_handles_chatter():
    text = "Вот результат: " + json.dumps(GOOD_ANSWER) + " — готово."
    assert parse_json_object(text)["score"] == 7.5


def test_parse_json_object_raises_on_garbage():
    with pytest.raises(ValueError):
        parse_json_object("никакого json здесь нет")


def test_analyze_repo_parses_mock_answer(make_repo, passed_security):
    llm = FakeLLM([json.dumps(GOOD_ANSWER)])
    analysis = analyze_repo(make_repo(), passed_security, llm, "prompts")
    assert isinstance(analysis, RepoAnalysis)
    assert analysis.score == 7.5
    assert llm.calls == 1


def test_analyze_repo_retries_then_excludes(make_repo, passed_security):
    llm = FakeLLM(["не json", "тоже не json"])
    assert analyze_repo(make_repo(), passed_security, llm, "prompts") is None
    assert llm.calls == 2


def test_analyze_repo_forces_input_full_name(make_repo, passed_security):
    wrong = {**GOOD_ANSWER, "full_name": "someone/else"}
    analysis = analyze_repo(make_repo("owner/repo"), passed_security, FakeLLM([json.dumps(wrong)]), "prompts")
    assert analysis.full_name == "owner/repo"


def test_prompt_contains_repo_facts(make_repo, passed_security):
    system, user = build_analysis_prompt(make_repo(readme_excerpt="Мой README"), passed_security, "prompts")
    assert "технический аналитик" in system
    assert "owner/repo" in user
    assert "Мой README" in user
    assert "critical=0" in repo_block(make_repo(), passed_security)


def test_groq_client_builds_model_chain():
    llm = GroqLLM(api_key="test-key", model="openai/gpt-oss-120b", fallbacks=["llama-3.3-70b-versatile", "openai/gpt-oss-120b"])
    assert llm.models == ["openai/gpt-oss-120b", "llama-3.3-70b-versatile"]
    assert llm.model == "openai/gpt-oss-120b"
