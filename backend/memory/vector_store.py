from functools import lru_cache

import chromadb

from config import get_settings

settings = get_settings()


class LocalEmbeddings:
    """Embeddings locaux : modèle MiniLM (ONNX) déjà embarqué par ChromaDB.

    Tourne sur CPU, aucune clé API ni appel réseau après le premier
    téléchargement du modèle (mis en cache par Chroma)."""

    def __init__(self) -> None:
        from chromadb.utils import embedding_functions

        self._fn = embedding_functions.DefaultEmbeddingFunction()

    def embed_query(self, text: str) -> list[float]:
        return [float(value) for value in self._fn([text])[0]]


@lru_cache
def get_embedder():
    if settings.embedding_provider == "local":
        return LocalEmbeddings()

    from langchain_openai import OpenAIEmbeddings

    return OpenAIEmbeddings(model=settings.openai_embedding_model, api_key=settings.openai_api_key)


def _collection_name() -> str:
    # Les deux providers produisent des vecteurs de dimensions différentes
    # (1536 pour OpenAI, 384 pour MiniLM) : une collection par provider évite
    # une erreur de dimension si on bascule l'un pour l'autre via l'env.
    return f"{settings.chroma_collection}_{settings.embedding_provider}"


@lru_cache
def get_collection():
    client = chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)
    return client.get_or_create_collection(_collection_name(), metadata={"hnsw:space": "cosine"})


def add_memory(memory_id: str, text: str, metadata: dict) -> None:
    """Persiste un souvenir (embedding + texte) pour la recherche sémantique future."""
    embedding = get_embedder().embed_query(text)
    get_collection().add(ids=[memory_id], documents=[text], metadatas=[metadata], embeddings=[embedding])


def search_memory(query: str, user_id: str, n_results: int = 5) -> list[str]:
    """Recherche par similarité cosinus les souvenirs pertinents pour la requête (RAG)."""
    collection = get_collection()
    if collection.count() == 0:
        return []

    embedding = get_embedder().embed_query(query)
    results = collection.query(
        query_embeddings=[embedding],
        n_results=min(n_results, collection.count()),
        where={"user_id": user_id},
    )
    documents = results.get("documents") or []
    return documents[0] if documents else []
