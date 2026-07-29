import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.session import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    """Identity Core : profil utilisateur (Phase 1 = utilisateur unique local)."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    tech_stack: Mapped[list] = mapped_column(JSON, default=list)
    preferences: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    facts: Mapped[list["Fact"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    messages: Mapped[list["Message"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Fact(Base):
    """Mémoire long terme : informations durables sur l'utilisateur (PostgreSQL)."""

    __tablename__ = "facts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    user: Mapped[User] = relationship(back_populates="facts")


class Message(Base):
    """Journal de conversation persistant (audit / reconstruction de mémoire vectorielle)."""

    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    session_id: Mapped[str] = mapped_column(String, index=True)
    role: Mapped[str] = mapped_column(String)  # "user" | "assistant"
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    user: Mapped[User] = relationship(back_populates="messages")


class Plan(Base):
    """Phase 2 : un plan d'action proposé par le planner, à valider avant exécution."""

    __tablename__ = "plans"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    session_id: Mapped[str] = mapped_column(String, index=True)
    goal: Mapped[str] = mapped_column(Text)
    # pending (en attente de validation) -> approved -> running -> done | failed
    status: Mapped[str] = mapped_column(String, default="pending")
    # Synthèse en langage naturel des résultats, générée une fois le plan
    # "done" (voir agent/executor.py). None si le plan a échoué ou si la
    # synthèse elle-même a échoué (les résultats bruts par étape restent
    # disponibles dans tous les cas).
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    steps: Mapped[list["PlanStep"]] = relationship(
        back_populates="plan",
        cascade="all, delete-orphan",
        order_by="PlanStep.step_order",
    )


class PlanStep(Base):
    """Une étape d'un plan : un appel de tool précis, avec son statut d'exécution."""

    __tablename__ = "plan_steps"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    plan_id: Mapped[str] = mapped_column(ForeignKey("plans.id"), index=True)
    step_order: Mapped[int] = mapped_column(Integer)
    tool: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text)
    args: Mapped[dict] = mapped_column(JSON, default=dict)
    # pending -> running -> done | failed
    status: Mapped[str] = mapped_column(String, default="pending")
    result: Mapped[str | None] = mapped_column(Text, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    plan: Mapped[Plan] = relationship(back_populates="steps")
