import json
from functools import lru_cache

import redis

from config import get_settings

settings = get_settings()


@lru_cache
def get_client() -> redis.Redis:
    return redis.Redis.from_url(settings.redis_url, decode_responses=True)


def _key(session_id: str) -> str:
    return f"session:{session_id}:history"


def get_history(session_id: str) -> list[dict]:
    """Historique de conversation de la session active (mémoire court terme)."""
    raw = get_client().lrange(_key(session_id), 0, -1)
    return [json.loads(item) for item in raw]


def append_message(session_id: str, role: str, content: str) -> None:
    client = get_client()
    key = _key(session_id)
    client.rpush(key, json.dumps({"role": role, "content": content}))
    client.expire(key, settings.short_term_ttl_seconds)
