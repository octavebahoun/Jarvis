from datetime import datetime

from pydantic import BaseModel

from db.models import Automation, Plan


class PlanStepResponse(BaseModel):
    id: str
    tool: str
    description: str
    status: str
    result: str | None = None
    error: str | None = None


class PlanResponse(BaseModel):
    id: str
    session_id: str
    goal: str
    status: str
    summary: str | None = None
    steps: list[PlanStepResponse]


def plan_to_response(plan: Plan) -> PlanResponse:
    return PlanResponse(
        id=plan.id,
        session_id=plan.session_id,
        goal=plan.goal,
        status=plan.status,
        summary=plan.summary,
        steps=[
            PlanStepResponse(
                id=step.id,
                tool=step.tool,
                description=step.description,
                status=step.status,
                result=step.result,
                error=step.error,
            )
            for step in plan.steps
        ],
    )


class AutomationResponse(BaseModel):
    id: str
    name: str
    schedule: str
    task: str
    active: bool
    last_run_at: datetime | None = None
    last_run_status: str | None = None
    last_run_plan_id: str | None = None


def automation_to_response(automation: Automation) -> AutomationResponse:
    return AutomationResponse(
        id=automation.id,
        name=automation.name,
        schedule=automation.schedule,
        task=automation.task,
        active=automation.active,
        last_run_at=automation.last_run_at,
        last_run_status=automation.last_run_status,
        last_run_plan_id=automation.last_run_plan_id,
    )
