import logging

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from sqlalchemy.orm import Session

import tools
from agent import reasoning
from db.models import Plan
from tasks import task_store

logger = logging.getLogger(__name__)


class PlanNotApprovedError(RuntimeError):
    """Un plan doit être approuvé (status == "approved") avant exécution."""


def _build_summary_prompt(plan: Plan) -> list[BaseMessage]:
    results_block = "\n".join(f"- {step.description} ({step.tool}) : {step.result}" for step in plan.steps)
    return [
        SystemMessage(
            content=(
                "Tu es Jarvis. Un plan d'actions vient d'être exécuté pour répondre à la "
                "demande de l'utilisateur. Rédige une réponse claire et directe à partir des "
                "résultats ci-dessous, comme si tu répondais directement à sa demande initiale "
                "— ne te contente pas de lister les résultats bruts."
            )
        ),
        HumanMessage(content=f"Demande initiale : {plan.goal}\n\nRésultats obtenus :\n{results_block}"),
    ]


def execute_plan(db: Session, plan: Plan) -> Plan:
    """Exécute un plan déjà validé par l'utilisateur, étape par étape, en
    appelant les tools du registre. S'arrête à la première étape en échec :
    le plan passe en "failed", les étapes suivantes restent "pending".

    Une fois toutes les étapes réussies, une synthèse en langage naturel des
    résultats est générée et stockée sur `plan.summary` — si cette synthèse
    échoue, le plan reste "done" quand même (les résultats bruts par étape
    restent disponibles dans tous les cas)."""
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

    try:
        summary = reasoning.generate_reply(_build_summary_prompt(plan))
        task_store.set_plan_summary(db, plan, summary)
    except Exception:
        logger.exception("Échec de la synthèse finale du plan %s (résultats bruts par étape disponibles).", plan.id)

    task_store.set_plan_status(db, plan, "done")
    return plan
