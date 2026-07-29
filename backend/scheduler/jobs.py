from datetime import datetime, timezone

from agent import proactive
from db.session import SessionLocal
from scheduler import registry
from tasks.worker import celery_app


def _run_tick(now: datetime) -> int:
    """Logique pure, séparée de la tâche Celery — mêmes raisons que
    tasks/worker.py::_run_plan (testable sans broker). Ne contient aucune
    logique métier : cherche les automatisations dues et délègue tout à
    agent/proactive.py, cf. phase3.md."""
    db = SessionLocal()
    try:
        due = registry.due_automations(db, now)
        for automation in due:
            proactive.run_automation(db, automation)
        return len(due)
    finally:
        db.close()


@celery_app.task(name="scheduler.tick")
def tick() -> int:
    return _run_tick(datetime.now(timezone.utc))
