import pytest

import tools.web_search as web_search_module
from tools.web_search import WebSearchTool


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


class _FailingResponse(_FakeResponse):
    def raise_for_status(self):
        raise RuntimeError("upstream error (401 Unauthorized)")


def test_web_search_formats_results(monkeypatch):
    monkeypatch.setattr(web_search_module.settings, "tavily_api_key", "tvly-test")

    captured = {}

    def fake_post(url, json, timeout):
        captured["url"] = url
        captured["query"] = json["query"]
        return _FakeResponse(
            {
                "results": [
                    {"title": "Résultat 1", "url": "https://example.com/1", "content": "Contenu 1"},
                    {"title": "Résultat 2", "url": "https://example.com/2", "content": "Contenu 2"},
                ]
            }
        )

    monkeypatch.setattr(web_search_module.httpx, "post", fake_post)

    result = WebSearchTool().run(query="meilleur framework python 2026")

    assert captured["query"] == "meilleur framework python 2026"
    assert captured["url"] == web_search_module.TAVILY_SEARCH_URL
    assert "Résultat 1" in result
    assert "https://example.com/1" in result
    assert "Résultat 2" in result


def test_web_search_handles_no_results(monkeypatch):
    monkeypatch.setattr(web_search_module.httpx, "post", lambda *a, **k: _FakeResponse({"results": []}))

    result = WebSearchTool().run(query="xyzzy_requete_sans_resultat")

    assert result == "Aucun résultat trouvé."


def test_web_search_raises_on_upstream_error(monkeypatch):
    monkeypatch.setattr(web_search_module.httpx, "post", lambda *a, **k: _FailingResponse({}))

    with pytest.raises(RuntimeError):
        WebSearchTool().run(query="peu importe")
