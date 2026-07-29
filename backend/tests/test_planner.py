import pytest

from agent import planner


class _FakeResponse:
    def __init__(self, content):
        self.content = content


class _FakeLLM:
    def __init__(self, content):
        self._content = content

    def invoke(self, messages):
        return _FakeResponse(self._content)


def test_build_plan_returns_empty_steps_for_simple_question(monkeypatch):
    monkeypatch.setattr(planner.reasoning, "_get_llm", lambda: _FakeLLM('{"steps": []}'))

    plan = planner.build_plan("Quelle heure est-il ?")

    assert plan.steps == []


def test_build_plan_parses_valid_steps(monkeypatch):
    content = (
        '{"steps": [{"tool": "file_reader", "description": "Lire main.py", '
        '"args": {"path": "main.py"}}]}'
    )
    monkeypatch.setattr(planner.reasoning, "_get_llm", lambda: _FakeLLM(content))

    plan = planner.build_plan("Analyse main.py")

    assert len(plan.steps) == 1
    assert plan.steps[0].tool == "file_reader"
    assert plan.steps[0].args == {"path": "main.py"}


def test_build_plan_strips_markdown_code_fence(monkeypatch):
    content = '```json\n{"steps": []}\n```'
    monkeypatch.setattr(planner.reasoning, "_get_llm", lambda: _FakeLLM(content))

    plan = planner.build_plan("Bonjour")

    assert plan.steps == []


def test_build_plan_ignores_trailing_garbage_after_valid_json(monkeypatch):
    """Certains modèles gratuits ajoutent un fragment parasite après un JSON
    par ailleurs valide (ex. un crochet fermant en trop) — vu en conditions
    réelles (worker, automatisation Phase 3)."""
    content = (
        '{"steps": [{"tool": "web_search", "description": "Recherche X", '
        '"args": {"query": "x"}}]}]'
    )
    monkeypatch.setattr(planner.reasoning, "_get_llm", lambda: _FakeLLM(content))

    plan = planner.build_plan("Cherche X")

    assert len(plan.steps) == 1
    assert plan.steps[0].tool == "web_search"


def test_build_plan_raises_on_invalid_json(monkeypatch):
    monkeypatch.setattr(planner.reasoning, "_get_llm", lambda: _FakeLLM("ceci n'est pas du JSON"))

    with pytest.raises(planner.PlannerError):
        planner.build_plan("Fais quelque chose")


def test_build_plan_raises_on_unknown_tool(monkeypatch):
    content = '{"steps": [{"tool": "tool_qui_nexiste_pas", "description": "x", "args": {}}]}'
    monkeypatch.setattr(planner.reasoning, "_get_llm", lambda: _FakeLLM(content))

    with pytest.raises(planner.PlannerError):
        planner.build_plan("Fais quelque chose")
