import os
import sys
import uuid

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import controller  # noqa: E402
from main import app  # noqa: E402


@pytest.fixture
def client(monkeypatch):
    """Client de test FastAPI. Postgres et Redis restent réels (docker-compose) ;
    le LLM et la mémoire vectorielle sont simulés pour ne pas dépendre d'une clé
    OpenAI ni d'appels payants pendant les tests."""
    monkeypatch.setattr(controller.reasoning, "generate_reply", lambda messages: "Réponse de test.")
    monkeypatch.setattr(controller.reasoning, "stream_reply", lambda messages: iter(["Réponse ", "de test."]))
    monkeypatch.setattr(controller.vector_store, "search_memory", lambda *args, **kwargs: [])
    monkeypatch.setattr(controller.vector_store, "add_memory", lambda *args, **kwargs: None)

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def session_id() -> str:
    """Un session_id unique par test pour ne pas interférer avec l'historique Redis d'un autre test."""
    return str(uuid.uuid4())
