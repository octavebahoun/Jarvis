from celery import Celery
from celery.schedules import crontab

from agent.executor import execute_plan
from config import get_settings
from db.session import SessionLocal
from tasks import task_store

settings = get_settings()

celery_app = Celery("jarvis", broker=settings.celery_broker_url, backend=settings.celery_result_backend)

# Phase 3 : tick du scheduler proactif (scheduler/jobs.py), déclenché chaque
# minute par Celery Beat — la tâche elle-même détermine quelles automatisations
# sont dues (cf. scheduler/registry.py) plutôt que d'avoir une entrée
# beat_schedule par automatisation, qui obligerait à redémarrer Beat à chaque
# création/modification d'automatisation.
celery_app.conf.beat_schedule = {
    "automation-tick": {
        "task": "scheduler.tick",
        "schedule": crontab(minute="*"),
    }
}


def _run_plan(plan_id: str) -> str:
    """Logique pure, séparée de la tâche Celery pour rester testable sans
    passer par la machinerie Celery (pas de broker requis dans les tests).

    Les imports du module (agent.executor, db.session, tasks.task_store) sont
    volontairement au niveau du module et non déférés dans cette fonction :
    Celery n'ajoute le répertoire courant à sys.path que temporairement, le
    temps de charger `tasks.worker` (option -A) ; des imports déférés à
    l'intérieur de la fonction échouent (ModuleNotFoundError) une fois ce
    chemin retiré, au moment de l'exécution réelle d'une tâche."""
    db = SessionLocal()
    try:
        plan = task_store.get_plan(db, plan_id)
        if plan is None:
            raise ValueError(f"Plan introuvable : {plan_id}")

        execute_plan(db, plan)
        return plan.status
    finally:
        db.close()


@celery_app.task(name="tasks.execute_plan_task")
def execute_plan_task(plan_id: str) -> str:
    return _run_plan(plan_id)


# Importé en fin de module (et non en haut, à côté des autres imports) :
# scheduler/jobs.py importe `celery_app` depuis ce module pour enregistrer sa
# tâche via @celery_app.task, ce qui créerait un import circulaire si cet
# import arrivait avant que `celery_app` existe. Import direct (pas déferré
# dans une fonction) pour la même raison que les autres imports de ce fichier
# — cf. commentaire de `_run_plan` — Celery doit pouvoir résoudre la tâche
# "scheduler.tick" au chargement de l'app.
from scheduler import jobs  # noqa: E402,F401
