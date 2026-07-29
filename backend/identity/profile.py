from sqlalchemy.orm import Session

from config import get_settings
from db.models import User

settings = get_settings()


def get_or_create_user(db: Session, user_id: str | None = None) -> User:
    """Phase 1 = utilisateur unique local : on charge le profil par défaut ou on le crée."""
    user_id = user_id or settings.default_user_id

    user = db.get(User, user_id)
    if user is not None:
        return user

    user = User(id=user_id, username=user_id, tech_stack=[], preferences={})
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(
    db: Session,
    user: User,
    tech_stack: list[str] | None = None,
    preferences: dict | None = None,
) -> User:
    if tech_stack is not None:
        user.tech_stack = tech_stack
    if preferences is not None:
        user.preferences = {**user.preferences, **preferences}

    db.commit()
    db.refresh(user)
    return user
