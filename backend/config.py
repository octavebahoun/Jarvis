from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration centrale de l'API, chargée depuis les variables d'environnement."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    # "openai" (payant, GPT-4o) ou "openrouter" (modèles gratuits ":free").
    chat_provider: str = "openai"
    openrouter_api_key: str = ""
    openrouter_model: str = "meta-llama/llama-3.1-8b-instruct:free"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    database_url: str = "postgresql://jarvis:jarvis@localhost:5432/jarvis"

    redis_url: str = "redis://localhost:6379"
    short_term_ttl_seconds: int = 60 * 60 * 2  # 2h, cf. phase1.md

    chroma_host: str = "localhost"
    chroma_port: int = 8000
    chroma_collection: str = "jarvis_memory"

    # "openai" (API payante, text-embedding-3-small) ou "local" (ONNX MiniLM
    # embarqué dans ChromaDB, gratuit, tourne sur CPU sans clé API).
    embedding_provider: str = "openai"
    openai_embedding_model: str = "text-embedding-3-small"

    secret_key: str = "change-this-in-production"

    default_user_id: str = "default"


@lru_cache
def get_settings() -> Settings:
    return Settings()
