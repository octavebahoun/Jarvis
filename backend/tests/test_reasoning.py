from agent import reasoning


def test_get_llm_defaults_to_openai(monkeypatch):
    monkeypatch.setattr(reasoning.settings, "chat_provider", "openai")
    monkeypatch.setattr(reasoning.settings, "openai_model", "gpt-4o")
    monkeypatch.setattr(reasoning.settings, "openai_api_key", "sk-test-placeholder")

    llm = reasoning._get_llm()

    assert llm.model_name == "gpt-4o"
    assert llm.openai_api_base is None


def test_get_llm_switches_to_openrouter_via_settings(monkeypatch):
    monkeypatch.setattr(reasoning.settings, "chat_provider", "openrouter")
    monkeypatch.setattr(reasoning.settings, "openrouter_model", "meta-llama/llama-3.1-8b-instruct:free")
    monkeypatch.setattr(reasoning.settings, "openrouter_api_key", "sk-or-test-placeholder")
    monkeypatch.setattr(reasoning.settings, "openrouter_base_url", "https://openrouter.ai/api/v1")

    llm = reasoning._get_llm()

    assert llm.model_name == "meta-llama/llama-3.1-8b-instruct:free"
    assert llm.openai_api_base == "https://openrouter.ai/api/v1"
