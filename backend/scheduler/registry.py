from datetime import datetime

from croniter import croniter
from sqlalchemy.orm import Session

from db.models import Automation


def due_automations(db: Session, now: datetime) -> list[Automation]:
    """Automatisations actives dont l'expression cron matche la minute de
    `now` (secondes/microsecondes ignorées : le tick tourne une fois par
    minute, cf. scheduler/jobs.py)."""
    now = now.replace(second=0, microsecond=0)
    return [
        automation
        for automation in db.query(Automation).filter(Automation.active.is_(True)).all()
        if croniter.match(automation.schedule, now)
    ]
