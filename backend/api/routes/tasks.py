from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.deps import get_db
from api.schemas import PlanResponse, plan_to_response
from tasks import task_store
from tasks.worker import execute_plan_task

router = APIRouter()


@router.get("/tasks/{plan_id}", response_model=PlanResponse)
def get_task(plan_id: str, db: Session = Depends(get_db)) -> PlanResponse:
    plan = task_store.get_plan(db, plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan introuvable.")

    return plan_to_response(plan)


@router.post("/tasks/{plan_id}/approve", response_model=PlanResponse)
def approve_task(plan_id: str, db: Session = Depends(get_db)) -> PlanResponse:
    plan = task_store.get_plan(db, plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan introuvable.")
    if plan.status != "pending":
        raise HTTPException(
            status_code=409,
            detail=f"Le plan n'est pas en attente de validation (status={plan.status!r}).",
        )

    plan = task_store.set_plan_status(db, plan, "approved")
    execute_plan_task.delay(plan_id)

    return plan_to_response(plan)
