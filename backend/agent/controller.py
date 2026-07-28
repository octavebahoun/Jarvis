import uuid
from collections.abc import Iterator

from sqlalchemy.orm import Session

from agent import reasoning
from db.models import Message
from db.session import SessionLocal
from identity.profile import get_or_create_user
from memory import short_term, vector_store

# Marqueur de fin de flux en cas d'échec du LLM en cours de streaming : les
# entêtes HTTP (200) sont déjà envoyés à ce stade, on ne peut plus renvoyer un
# vrai code d'erreur, donc l'échec est signalé dans le flux lui-même.
STREAM_ERROR_MARKER = "\n\n<<JARVIS_STREAM_ERROR>>"


class AgentUnavailableError(RuntimeError):
    """Le LLM n'a pas pu répondre (clé API absente/invalide, service indisponible, etc.)."""


def handle_chat(db: Session, session_id: str, user_message: str, user_id: str | None = None) -> str:
    """Point d'entrée unique de l'agent : charge le contexte, raisonne, sauvegarde la mémoire."""
    user = get_or_create_user(db, user_id)

    history = short_term.get_history(session_id)
    relevant_memories = vector_store.search_memory(user_message, user_id=user.id)

    messages = reasoning.build_messages(user, history, relevant_memories, user_message)

    try:
        reply = reasoning.generate_reply(messages)
    except Exception as exc:
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

    vector_store.add_memory(
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
        relevant_memories = vector_store.search_memory(user_message, user_id=user.id)
        messages = reasoning.build_messages(user, history, relevant_memories, user_message)

        reply_parts: list[str] = []
        try:
            for chunk in reasoning.stream_reply(messages):
                reply_parts.append(chunk)
                yield chunk
        except Exception:
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

        vector_store.add_memory(
            memory_id=str(uuid.uuid4()),
            text=f"Utilisateur: {user_message}\nJarvis: {reply}",
            metadata={"user_id": user.id, "session_id": session_id},
        )
    finally:
        db.close()
