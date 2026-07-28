from sqlalchemy.orm import Session

from db.models import Plan, PlanStep


def create_plan(db: Session, user_id: str, session_id: str, goal: str, steps: list[dict]) -> Plan:
    """Persiste un plan et ses étapes avant toute exécution (traçabilité, cf. phase2.md).
    Statut initial "pending" : en attente de validation humaine."""
    plan = Plan(user_id=user_id, session_id=session_id, goal=goal, status="pending")
    plan.steps = [
        PlanStep(
            step_order=index,
            tool=step["tool"],
            description=step["description"],
            args=step.get("args", {}),
        )
        for index, step in enumerate(steps)
    ]

    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def get_plan(db: Session, plan_id: str) -> Plan | None:
    return db.get(Plan, plan_id)


def set_plan_status(db: Session, plan: Plan, status: str) -> Plan:
    plan.status = status
    db.commit()
    db.refresh(plan)
    return plan


def set_step_result(
    db: Session,
    step: PlanStep,
    status: str,
    result: str | None = None,
    error: str | None = None,
) -> PlanStep:
    step.status = status
    step.result = result
    step.error = error
    db.commit()
    db.refresh(step)
    return step
