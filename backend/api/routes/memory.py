from enum import Enum

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.deps import get_db
from config import get_settings
from memory import long_term, short_term

router = APIRouter()
settings = get_settings()


class MemoryType(str, Enum):
    short_term = "short_term"
    long_term = "long_term"


@router.get("/memory")
def get_memory(
    type: MemoryType = Query(MemoryType.long_term),
    session_id: str | None = None,
    db: Session = Depends(get_db),
) -> dict:
    if type is MemoryType.short_term:
        if not session_id:
            return {"items": []}
        return {"items": short_term.get_history(session_id)}

    facts = long_term.list_facts(db, user_id=settings.default_user_id)
    return {
        "items": [
            {"id": fact.id, "content": fact.content, "created_at": fact.created_at.isoformat()}
            for fact in facts
        ]
    }
