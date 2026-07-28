import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from api.schemas import plan_to_response
from db.session import SessionLocal
from tasks import task_store

router = APIRouter()

_TERMINAL_STATUSES = {"done", "failed"}
_POLL_INTERVAL_SECONDS = 1.0


@router.websocket("/ws/tasks/{plan_id}")
async def ws_task_status(websocket: WebSocket, plan_id: str) -> None:
    """Pousse l'état du plan au frontend jusqu'à ce qu'il atteigne un statut
    terminal (done/failed). Implémenté par polling DB plutôt que par un vrai
    pub/sub : l'exécution tourne dans un worker Celery, un processus séparé
    de l'API — le plus simple pour observer son avancement entre process est
    de relire régulièrement l'état persisté en base."""
    await websocket.accept()
    db = SessionLocal()
    last_payload = None

    try:
        while True:
            db.expire_all()  # sans ça, SQLAlchemy renverrait l'état mis en cache, pas l'état réel en base
            plan = task_store.get_plan(db, plan_id)

            if plan is None:
                await websocket.send_json({"error": "Plan introuvable."})
                break

            payload = plan_to_response(plan).model_dump()
            if payload != last_payload:
                await websocket.send_json(payload)
                last_payload = payload

            if plan.status in _TERMINAL_STATUSES:
                break

            await asyncio.sleep(_POLL_INTERVAL_SECONDS)
    except WebSocketDisconnect:
        pass
    finally:
        db.close()
