import uuid

from sqlalchemy.orm import Session

from agent import reasoning
from db.models import Message
from identity.profile import get_or_create_user
from memory import short_term, vector_store


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
