import tools.browser_automation as browser_module
from tools.browser_automation import BrowserAutomationTool


def test_browser_automation_enables_network_and_passes_url(monkeypatch):
    captured = {}

    def fake_run_in_container(**kwargs):
        captured.update(kwargs)
        return "contenu de la page"

    monkeypatch.setattr(browser_module, "run_in_container", fake_run_in_container)

    result = BrowserAutomationTool().run(url="https://example.com")

    assert result == "contenu de la page"
    # Contrairement à code_executor : le réseau doit rester activé.
    assert captured["network_disabled"] is False
    assert "https://example.com" in captured["command"][-1]


def test_browser_automation_passes_selector_when_given(monkeypatch):
    captured = {}
    monkeypatch.setattr(
        browser_module,
        "run_in_container",
        lambda **kwargs: captured.update(kwargs) or "ok",
    )

    BrowserAutomationTool().run(url="https://example.com", selector="h1")

    assert "h1" in captured["command"][-1]


def test_browser_automation_requires_validation():
    assert BrowserAutomationTool().requires_validation is True


def test_browser_automation_truncates_output(monkeypatch):
    monkeypatch.setattr(browser_module, "run_in_container", lambda **kwargs: "y" * 20_000)

    result = BrowserAutomationTool().run(url="https://example.com")

    assert len(result) == browser_module.MAX_OUTPUT_CHARS
