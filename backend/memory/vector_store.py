from functools import lru_cache

import chromadb
from langchain_openai import OpenAIEmbeddings

from config import get_settings

settings = get_settings()


@lru_cache
def get_collection():
    client = chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)
    return client.get_or_create_collection(settings.chroma_collection)


@lru_cache
def get_embedder() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(model="text-embedding-3-small", api_key=settings.openai_api_key)


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
