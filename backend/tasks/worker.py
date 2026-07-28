from celery import Celery

from config import get_settings

settings = get_settings()

celery_app = Celery("jarvis", broker=settings.celery_broker_url, backend=settings.celery_result_backend)


def _run_plan(plan_id: str) -> str:
    """Logique pure, séparée de la tâche Celery pour rester testable sans
    passer par la machinerie Celery (pas de broker requis dans les tests)."""
    from agent.executor import execute_plan
    from db.session import SessionLocal
    from tasks import task_store

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
