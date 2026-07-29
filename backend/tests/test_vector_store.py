from memory import vector_store


def test_get_embedder_defaults_to_openai(monkeypatch):
    vector_store.get_embedder.cache_clear()
    monkeypatch.setattr(vector_store.settings, "embedding_provider", "openai")
    monkeypatch.setattr(vector_store.settings, "openai_api_key", "sk-test-placeholder")

    from langchain_openai import OpenAIEmbeddings

    embedder = vector_store.get_embedder()

    assert isinstance(embedder, OpenAIEmbeddings)
    vector_store.get_embedder.cache_clear()


def test_get_embedder_switches_to_local_via_settings(monkeypatch):
    vector_store.get_embedder.cache_clear()
    monkeypatch.setattr(vector_store.settings, "embedding_provider", "local")

    embedder = vector_store.get_embedder()

    assert isinstance(embedder, vector_store.LocalEmbeddings)
    vector_store.get_embedder.cache_clear()


def test_collection_name_is_scoped_per_provider(monkeypatch):
    monkeypatch.setattr(vector_store.settings, "chroma_collection", "jarvis_memory")

    monkeypatch.setattr(vector_store.settings, "embedding_provider", "openai")
    openai_name = vector_store._collection_name()

    monkeypatch.setattr(vector_store.settings, "embedding_provider", "local")
    local_name = vector_store._collection_name()

    assert openai_name != local_name
    assert openai_name == "jarvis_memory_openai"
    assert local_name == "jarvis_memory_local"
