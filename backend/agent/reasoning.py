from collections.abc import Iterator

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from config import get_settings
from db.models import User

settings = get_settings()


def _system_prompt(user: User, relevant_memories: list[str]) -> str:
    memories_block = "\n".join(f"- {memory}" for memory in relevant_memories) or "Aucun souvenir pertinent."
    tech_stack = ", ".join(user.tech_stack) or "non renseignée"

    return (
        "Tu es Jarvis, l'assistant IA personnel de l'utilisateur. Réponds en tenant compte "
        "de son profil et de ses souvenirs pertinents, avec un style direct et actionnable.\n\n"
        f"Profil utilisateur : {user.username} (stack : {tech_stack}).\n"
        f"Préférences : {user.preferences or 'aucune'}.\n\n"
        f"Souvenirs pertinents :\n{memories_block}"
    )


def build_messages(
    user: User,
    history: list[dict],
    relevant_memories: list[str],
    user_message: str,
) -> list[BaseMessage]:
    """Construit le prompt enrichi : profil + mémoire court terme + mémoire vectorielle."""
    messages: list[BaseMessage] = [SystemMessage(content=_system_prompt(user, relevant_memories))]

    for entry in history:
        message_cls = HumanMessage if entry["role"] == "user" else AIMessage
        messages.append(message_cls(content=entry["content"]))

    messages.append(HumanMessage(content=user_message))
    return messages


def generate_reply(messages: list[BaseMessage]) -> str:
    llm = ChatOpenAI(model=settings.openai_model, api_key=settings.openai_api_key)
    response = llm.invoke(messages)
    return str(response.content)


def stream_reply(messages: list[BaseMessage]) -> Iterator[str]:
    """Variante streaming : yield la réponse au fur et à mesure qu'elle est générée."""
    llm = ChatOpenAI(model=settings.openai_model, api_key=settings.openai_api_key)
    for chunk in llm.stream(messages):
        if chunk.content:
            yield str(chunk.content)
