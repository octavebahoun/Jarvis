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

    # Phase 2 — Tool System : répertoire auquel file_reader (et les futurs
    # tools fichiers) sont strictement limités. Jamais d'accès hors de ce dossier.
    sandbox_path: str = "./sandbox"

    # Phase 2 — tool web_search : clé API Tavily (gratuite, tavily.com).
    tavily_api_key: str = ""

    # Phase 2 — tool code_executor : container jetable, réseau désactivé.
    code_executor_image: str = "python:3.11-slim"
    code_executor_timeout_seconds: int = 10
    code_executor_memory_limit: str = "256m"
    code_executor_cpu_limit: float = 0.5

    # Phase 2 — tool browser_automation (Playwright) : container jetable,
    # réseau activé (nécessaire pour atteindre de vrais sites).
    browser_automation_image: str = "mcr.microsoft.com/playwright/python:v1.49.0-noble"
    browser_automation_timeout_seconds: int = 30
    browser_automation_memory_limit: str = "512m"
    browser_automation_cpu_limit: float = 1.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
