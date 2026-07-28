from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from agent.controller import handle_chat
from api.deps import get_db

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_id: str


class ChatResponse(BaseModel):
    reply: str
    session_id: str


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    reply = handle_chat(db, session_id=payload.session_id, user_message=payload.message)
    return ChatResponse(reply=reply, session_id=payload.session_id)
