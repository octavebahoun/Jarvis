from pydantic import BaseModel

from db.models import Plan


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
