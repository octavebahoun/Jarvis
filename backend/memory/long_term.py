from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import Fact


def add_fact(db: Session, user_id: str, content: str) -> Fact:
    fact = Fact(user_id=user_id, content=content)
    db.add(fact)
    db.commit()
    db.refresh(fact)
    return fact


def list_facts(db: Session, user_id: str) -> list[Fact]:
    stmt = select(Fact).where(Fact.user_id == user_id).order_by(Fact.created_at.desc())
    return list(db.scalars(stmt))
