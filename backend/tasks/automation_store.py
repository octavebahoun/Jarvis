from datetime import datetime

from sqlalchemy.orm import Session

from db.models import Automation


def create_automation(
    db: Session, user_id: str, name: str, schedule: str, task: str, active: bool = True
) -> Automation:
    automation = Automation(user_id=user_id, name=name, schedule=schedule, task=task, active=active)
    db.add(automation)
    db.commit()
    db.refresh(automation)
    return automation


def list_automations(db: Session, user_id: str) -> list[Automation]:
    return (
        db.query(Automation)
        .filter(Automation.user_id == user_id)
        .order_by(Automation.created_at)
        .all()
    )


def get_automation(db: Session, automation_id: str) -> Automation | None:
    return db.get(Automation, automation_id)


def set_automation_active(db: Session, automation: Automation, active: bool) -> Automation:
    automation.active = active
    db.commit()
    db.refresh(automation)
    return automation


def record_automation_run(
    db: Session, automation: Automation, status: str, plan_id: str | None, ran_at: datetime
) -> Automation:
    automation.last_run_at = ran_at
    automation.last_run_status = status
    automation.last_run_plan_id = plan_id
    db.commit()
    db.refresh(automation)
    return automation
