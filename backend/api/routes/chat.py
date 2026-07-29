from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from agent.controller import AgentUnavailableError, handle_chat_or_plan, stream_chat_or_plan
from api.deps import get_db
from api.schemas import AutomationResponse, PlanResponse, automation_to_response, plan_to_response

router = APIRouter()


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    session_id: str = Field(min_length=1)


class ChatResponse(BaseModel):
    # "reply" (Phase 1, inchangé) | "plan" (Phase 2, en attente d'approbation)
    # | "automation" (Phase 3, programmée sans validation)
    type: str
    session_id: str
    reply: str | None = None
    plan: PlanResponse | None = None
    automation: AutomationResponse | None = None


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    try:
        outcome = handle_chat_or_plan(db, session_id=payload.session_id, user_message=payload.message)
    except AgentUnavailableError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    if outcome["type"] == "automation":
        return ChatResponse(
            type="automation",
            session_id=payload.session_id,
            automation=automation_to_response(outcome["automation"]),
        )

    if outcome["type"] == "plan":
        return ChatResponse(type="plan", session_id=payload.session_id, plan=plan_to_response(outcome["plan"]))

    return ChatResponse(type="reply", session_id=payload.session_id, reply=outcome["reply"])


@router.post("/chat/stream")
def chat_stream(payload: ChatRequest) -> StreamingResponse:
    """Comme /chat, mais renvoie la réponse en flux (texte brut) au fur et à
    mesure de sa génération, plutôt que d'attendre la réponse complète.

    Si une automatisation est programmée (Phase 3) ou qu'un plan d'action est
    nécessaire (Phase 2), le flux contient un seul chunk : AUTOMATION_MARKER +
    id, ou PLAN_MARKER + id du plan — le frontend va chercher les détails via
    GET /automations/:id ou GET /tasks/:id plutôt que d'afficher ce chunk
    comme du texte de chat."""
    return StreamingResponse(
        stream_chat_or_plan(session_id=payload.session_id, user_message=payload.message),
        media_type="text/plain",
    )
