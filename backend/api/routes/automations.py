from croniter import croniter
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from api.deps import get_db
from api.schemas import AutomationResponse, automation_to_response
from identity.profile import get_or_create_user
from tasks import automation_store

router = APIRouter()


class AutomationCreateRequest(BaseModel):
    name: str
    schedule: str
    task: str
    active: bool = True

    @field_validator("schedule")
    @classmethod
    def _validate_cron(cls, value: str) -> str:
        if not croniter.is_valid(value):
            raise ValueError(f"Expression cron invalide : {value!r}")
        return value


@router.post("/automations", response_model=AutomationResponse)
def create_automation(payload: AutomationCreateRequest, db: Session = Depends(get_db)) -> AutomationResponse:
    user = get_or_create_user(db)
    automation = automation_store.create_automation(
        db,
        user_id=user.id,
        name=payload.name,
        schedule=payload.schedule,
        task=payload.task,
        active=payload.active,
    )
    return automation_to_response(automation)


@router.get("/automations", response_model=list[AutomationResponse])
def list_automations(db: Session = Depends(get_db)) -> list[AutomationResponse]:
    user = get_or_create_user(db)
    return [automation_to_response(automation) for automation in automation_store.list_automations(db, user.id)]


@router.get("/automations/{automation_id}", response_model=AutomationResponse)
def get_automation(automation_id: str, db: Session = Depends(get_db)) -> AutomationResponse:
    automation = automation_store.get_automation(db, automation_id)
    if automation is None:
        raise HTTPException(status_code=404, detail="Automatisation introuvable.")

    return automation_to_response(automation)


@router.put("/automations/{automation_id}/toggle", response_model=AutomationResponse)
def toggle_automation(automation_id: str, db: Session = Depends(get_db)) -> AutomationResponse:
    automation = automation_store.get_automation(db, automation_id)
    if automation is None:
        raise HTTPException(status_code=404, detail="Automatisation introuvable.")

    automation = automation_store.set_automation_active(db, automation, not automation.active)
    return automation_to_response(automation)
