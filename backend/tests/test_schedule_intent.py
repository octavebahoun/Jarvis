from datetime import datetime, timezone

import pytest

from agent import schedule_intent


class _FakeResponse:
    def __init__(self, content):
        self.content = content


class _FakeLLM:
    def __init__(self, content):
        self._content = content

    def invoke(self, messages):
        return _FakeResponse(self._content)


NOW = datetime(2026, 7, 29, 14, 30, tzinfo=timezone.utc)


def test_detect_schedule_intent_returns_not_scheduled_for_immediate_request(monkeypatch):
    content = '{"scheduled": false, "recurring": false, "cron": null, "name": null, "task": null}'
    monkeypatch.setattr(schedule_intent.reasoning, "_get_llm", lambda: _FakeLLM(content))

    intent = schedule_intent.detect_schedule_intent("Quelle heure est-il ?", NOW)

    assert intent.scheduled is False


def test_detect_schedule_intent_parses_one_shot_request(monkeypatch):
    content = (
        '{"scheduled": true, "recurring": false, "cron": "32 14 29 7 *", '
        '"name": "Recherche IA", "task": "cherche les dernières nouvelles sur l\'IA"}'
    )
    monkeypatch.setattr(schedule_intent.reasoning, "_get_llm", lambda: _FakeLLM(content))

    intent = schedule_intent.detect_schedule_intent("cherche les news sur l'IA dans 2 minutes", NOW)

    assert intent.scheduled is True
    assert intent.recurring is False
    assert intent.cron == "32 14 29 7 *"
    assert intent.task == "cherche les dernières nouvelles sur l'IA"


def test_detect_schedule_intent_parses_recurring_request(monkeypatch):
    content = (
        '{"scheduled": true, "recurring": true, "cron": "0 9 * * *", '
        '"name": "Veille tech", "task": "cherche les news IA"}'
    )
    monkeypatch.setattr(schedule_intent.reasoning, "_get_llm", lambda: _FakeLLM(content))

    intent = schedule_intent.detect_schedule_intent("cherche les news IA tous les matins", NOW)

    assert intent.scheduled is True
    assert intent.recurring is True


def test_detect_schedule_intent_strips_markdown_code_fence(monkeypatch):
    content = '```json\n{"scheduled": false, "recurring": false, "cron": null, "name": null, "task": null}\n```'
    monkeypatch.setattr(schedule_intent.reasoning, "_get_llm", lambda: _FakeLLM(content))

    intent = schedule_intent.detect_schedule_intent("Bonjour", NOW)

    assert intent.scheduled is False


def test_detect_schedule_intent_ignores_trailing_garbage_after_valid_json(monkeypatch):
    content = (
        '{"scheduled": true, "recurring": false, "cron": "32 14 29 7 *", '
        '"name": "Recherche IA", "task": "cherche les news IA"}]'
    )
    monkeypatch.setattr(schedule_intent.reasoning, "_get_llm", lambda: _FakeLLM(content))

    intent = schedule_intent.detect_schedule_intent("cherche les news IA dans 2 min", NOW)

    assert intent.scheduled is True
    assert intent.cron == "32 14 29 7 *"


def test_detect_schedule_intent_raises_on_invalid_json(monkeypatch):
    monkeypatch.setattr(schedule_intent.reasoning, "_get_llm", lambda: _FakeLLM("ceci n'est pas du JSON"))

    with pytest.raises(schedule_intent.ScheduleIntentError):
        schedule_intent.detect_schedule_intent("Fais quelque chose", NOW)


def test_detect_schedule_intent_raises_on_invalid_cron(monkeypatch):
    content = '{"scheduled": true, "recurring": false, "cron": "pas un cron", "name": null, "task": null}'
    monkeypatch.setattr(schedule_intent.reasoning, "_get_llm", lambda: _FakeLLM(content))

    with pytest.raises(schedule_intent.ScheduleIntentError):
        schedule_intent.detect_schedule_intent("dans 2 minutes fais un truc", NOW)
