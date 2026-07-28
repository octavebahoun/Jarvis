from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config import get_settings

settings = get_settings()

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    """Crée les tables manquantes. Suffisant pour le MVP (Phase 1); Alembic prendra le relai en Phase 2."""
    from db import models  # noqa: F401 (enregistre les modèles sur Base avant create_all)

    Base.metadata.create_all(bind=engine)
