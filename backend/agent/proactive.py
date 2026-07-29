import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

import tools
from agent import planner
from agent.executor import execute_plan
from db.models import Automation, Plan
from tasks import automation_store, task_store

logger = logging.getLogger(__name__)


class AutomationBlockedError(RuntimeError):
    """Levée quand le plan proposé pour une automatisation contient un tool
    nécessitant une validation humaine (code_executor, browser_automation) —
    une exécution proactive ne peut jamais auto-approuver ce genre d'action,
    cf. phase3.md : "les automatisations proactives ne peuvent pas exécuter
    code_executor sans session active de l'utilisateur"."""


def run_automation(db: Session, automation: Automation) -> Plan | None:
    """Construit le plan de l'automatisation via le planner (même mécanisme
    qu'une demande utilisateur en Phase 2), l'auto-approuve puis l'exécute —
    sans validation humaine, sauf si une étape nécessite un tool sensible, ce
    qui bloque l'exécution entière plutôt que de l'auto-approuver.

    Toute erreur (planner, tool bloquant, exécution) est journalisée sur
    l'automatisation (`last_run_status`) sans jamais remonter d'exception :
    le scheduler doit pouvoir traiter les automatisations suivantes même si
    celle-ci échoue."""
    ran_at = datetime.now(timezone.utc)

    try:
        proposed = planner.build_plan(automation.task)
        for step in proposed.steps:
            if tools.get_tool(step.tool).requires_validation:
                raise AutomationBlockedError(
                    f"Le tool {step.tool!r} nécessite une validation humaine, "
                    "impossible en exécution proactive."
                )

        plan = task_store.create_plan(
            db,
            user_id=automation.user_id,
            session_id=f"automation:{automation.id}",
            goal=automation.task,
            steps=[step.model_dump() for step in proposed.steps],
        )
        task_store.set_plan_status(db, plan, "approved")
        execute_plan(db, plan)

        automation_store.record_automation_run(db, automation, plan.status, plan.id, ran_at)
        return plan

    except Exception:
        logger.exception("Échec de l'automatisation %s (%s)", automation.id, automation.name)
        automation_store.record_automation_run(db, automation, "failed", None, ran_at)
        return None
