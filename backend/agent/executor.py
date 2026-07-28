import logging

from sqlalchemy.orm import Session

import tools
from db.models import Plan
from tasks import task_store

logger = logging.getLogger(__name__)


class PlanNotApprovedError(RuntimeError):
    """Un plan doit être approuvé (status == "approved") avant exécution."""


def execute_plan(db: Session, plan: Plan) -> Plan:
    """Exécute un plan déjà validé par l'utilisateur, étape par étape, en
    appelant les tools du registre. S'arrête à la première étape en échec :
    le plan passe en "failed", les étapes suivantes restent "pending"."""
    if plan.status != "approved":
        raise PlanNotApprovedError(f"Le plan {plan.id} n'est pas approuvé (status={plan.status!r}).")

    task_store.set_plan_status(db, plan, "running")

    for step in plan.steps:
        task_store.set_step_result(db, step, status="running")

        try:
            tool = tools.get_tool(step.tool)
            result = tool.run(**step.args)
        except Exception as exc:
            logger.exception("Échec de l'étape %s (tool=%s) du plan %s", step.id, step.tool, plan.id)
            task_store.set_step_result(db, step, status="failed", error=str(exc))
            task_store.set_plan_status(db, plan, "failed")
            return plan

        task_store.set_step_result(db, step, status="done", result=result)

    task_store.set_plan_status(db, plan, "done")
    return plan
