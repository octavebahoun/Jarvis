import logging
import uuid
from collections.abc import Iterator

from sqlalchemy.orm import Session

from agent import planner, reasoning
from db.models import Message, Plan, User
from db.session import SessionLocal
from identity.profile import get_or_create_user
from memory import short_term, vector_store
from tasks import task_store

logger = logging.getLogger(__name__)

# Marqueur de fin de flux en cas d'échec du LLM en cours de streaming : les
# entêtes HTTP (200) sont déjà envoyés à ce stade, on ne peut plus renvoyer un
# vrai code d'erreur, donc l'échec est signalé dans le flux lui-même.
STREAM_ERROR_MARKER = "\n\n<<JARVIS_STREAM_ERROR>>"

# Phase 2 : un plan proposé est signalé dans le flux par ce marqueur suivi de
# l'id du plan (le frontend va chercher les détails via GET /tasks/:id).
PLAN_MARKER = "\n\n<<JARVIS_PLAN>>"


class AgentUnavailableError(RuntimeError):
    """Le LLM n'a pas pu répondre (clé API absente/invalide, service indisponible, etc.)."""


def _safe_search_memory(user_message: str, user_id: str) -> list[str]:
    """La mémoire vectorielle est un enrichissement, pas une dépendance critique :
    si Chroma ou l'embedder échoue (ex. téléchargement du modèle local qui
    time-out sur un réseau lent), le chat continue sans contexte RAG plutôt
    que de planter toute la requête."""
    try:
        return vector_store.search_memory(user_message, user_id=user_id)
    except Exception:
        logger.exception("Recherche mémoire vectorielle indisponible, poursuite sans contexte RAG.")
        return []


def _safe_add_memory(memory_id: str, text: str, metadata: dict) -> None:
    try:
        vector_store.add_memory(memory_id=memory_id, text=text, metadata=metadata)
    except Exception:
        logger.exception("Échec de l'indexation du souvenir dans la mémoire vectorielle (ignoré).")


def _maybe_create_plan(db: Session, user: User, session_id: str, user_message: str) -> Plan | None:
    """Demande au planner si `user_message` nécessite des tools. Si oui,
    persiste le plan (statut "pending", en attente de validation humaine) et
    le retourne. Si le planner échoue ou ne propose aucune étape, retourne
    None : l'appelant doit alors retomber sur le chat simple (Phase 1)."""
    try:
        proposed = planner.build_plan(user_message)
    except Exception:
        logger.exception("Échec du planner, retour au chat simple.")
        return None

    if not proposed.steps:
        return None

    return task_store.create_plan(
        db,
        user_id=user.id,
        session_id=session_id,
        goal=user_message,
        steps=[{"tool": step.tool, "description": step.description, "args": step.args} for step in proposed.steps],
    )


def handle_chat_or_plan(db: Session, session_id: str, user_message: str, user_id: str | None = None) -> dict:
    """Point d'entrée Phase 2 pour /chat : décide d'abord si un plan d'action
    est nécessaire. Si oui, le persiste et le renvoie (en attente
    d'approbation) sans appeler le LLM de chat. Sinon, comportement Phase 1
    inchangé via handle_chat()."""
    user = get_or_create_user(db, user_id)

    plan = _maybe_create_plan(db, user, session_id, user_message)
    if plan is not None:
        short_term.append_message(session_id, "user", user_message)
        return {"type": "plan", "plan": plan}

    reply = handle_chat(db, session_id=session_id, user_message=user_message, user_id=user_id)
    return {"type": "reply", "reply": reply}


def stream_chat_or_plan(session_id: str, user_message: str, user_id: str | None = None) -> Iterator[str]:
    """Équivalent streaming de handle_chat_or_plan. Si un plan est nécessaire,
    yield un unique chunk (marqueur + id du plan) et s'arrête — sinon délègue
    entièrement à stream_chat(), inchangé."""
    db = SessionLocal()
    try:
        user = get_or_create_user(db, user_id)
        plan = _maybe_create_plan(db, user, session_id, user_message)

        if plan is not None:
            short_term.append_message(session_id, "user", user_message)
            yield f"{PLAN_MARKER}{plan.id}"
            return
    finally:
        db.close()

    yield from stream_chat(session_id, user_message, user_id)


def handle_chat(db: Session, session_id: str, user_message: str, user_id: str | None = None) -> str:
    """Point d'entrée unique de l'agent : charge le contexte, raisonne, sauvegarde la mémoire."""
    user = get_or_create_user(db, user_id)

    history = short_term.get_history(session_id)
    relevant_memories = _safe_search_memory(user_message, user_id=user.id)

    messages = reasoning.build_messages(user, history, relevant_memories, user_message)

    try:
        reply = reasoning.generate_reply(messages)
    except Exception as exc:
        logger.exception("Échec de l'appel LLM (chat_provider=%s)", reasoning.settings.chat_provider)
        raise AgentUnavailableError("Le LLM n'a pas pu générer de réponse.") from exc

    short_term.append_message(session_id, "user", user_message)
    short_term.append_message(session_id, "assistant", reply)

    db.add_all(
        [
            Message(user_id=user.id, session_id=session_id, role="user", content=user_message),
            Message(user_id=user.id, session_id=session_id, role="assistant", content=reply),
        ]
    )
    db.commit()

    _safe_add_memory(
        memory_id=str(uuid.uuid4()),
        text=f"Utilisateur: {user_message}\nJarvis: {reply}",
        metadata={"user_id": user.id, "session_id": session_id},
    )

    return reply


def stream_chat(session_id: str, user_message: str, user_id: str | None = None) -> Iterator[str]:
    """Variante streaming de handle_chat : yield la réponse morceau par morceau,
    puis persiste l'échange complet une fois le flux terminé.

    Gère sa propre session DB (plutôt que Depends(get_db)) : avec une réponse
    HTTP en streaming, FastAPI referme les dépendances dès que la route
    retourne l'objet StreamingResponse, bien avant que ce générateur n'ait fini
    de produire les morceaux et d'écrire en base."""
    db = SessionLocal()
    try:
        user = get_or_create_user(db, user_id)
        history = short_term.get_history(session_id)
        relevant_memories = _safe_search_memory(user_message, user_id=user.id)
        messages = reasoning.build_messages(user, history, relevant_memories, user_message)

        reply_parts: list[str] = []
        try:
            for chunk in reasoning.stream_reply(messages):
                reply_parts.append(chunk)
                yield chunk
        except Exception:
            logger.exception("Échec de l'appel LLM en streaming (chat_provider=%s)", reasoning.settings.chat_provider)
            yield STREAM_ERROR_MARKER
            return

        reply = "".join(reply_parts)

        short_term.append_message(session_id, "user", user_message)
        short_term.append_message(session_id, "assistant", reply)

        db.add_all(
            [
                Message(user_id=user.id, session_id=session_id, role="user", content=user_message),
                Message(user_id=user.id, session_id=session_id, role="assistant", content=reply),
            ]
        )
        db.commit()

        _safe_add_memory(
            memory_id=str(uuid.uuid4()),
            text=f"Utilisateur: {user_message}\nJarvis: {reply}",
            metadata={"user_id": user.id, "session_id": session_id},
        )
    finally:
        db.close()
