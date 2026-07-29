import json
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


def _get_llm() -> ChatOpenAI:
    if settings.chat_provider == "openrouter":
        return ChatOpenAI(
            model=settings.openrouter_model,
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
        )

    return ChatOpenAI(model=settings.openai_model, api_key=settings.openai_api_key)


def strip_json_code_fence(text: str) -> str:
    """Certains modèles entourent leur JSON de ```json ... ``` malgré la
    consigne de répondre en JSON brut — utilisé par tout module qui fait
    parler le LLM en JSON (planner.py, schedule_intent.py)."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else ""
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
    return text.strip()


def parse_json_object(text: str) -> dict:
    """Parse le premier objet JSON valide en tête de `text`, en ignorant tout
    contenu superflu après (certains modèles — notamment les modèles gratuits
    OpenRouter — ajoutent parfois un fragment parasite après un JSON par
    ailleurs valide, ex. un crochet fermant en trop ; `json.loads` rejette ça
    en bloc alors que le JSON utile est parfaitement lisible). Appeler
    `strip_json_code_fence` avant : `raw_decode` ne tolère pas d'espace/retour
    à la ligne en tête, contrairement à `json.loads`."""
    obj, _ = json.JSONDecoder().raw_decode(text)
    return obj


def generate_reply(messages: list[BaseMessage]) -> str:
    response = _get_llm().invoke(messages)
    return str(response.content)


def stream_reply(messages: list[BaseMessage]) -> Iterator[str]:
    """Variante streaming : yield la réponse au fur et à mesure qu'elle est générée."""
    for chunk in _get_llm().stream(messages):
        if chunk.content:
            yield str(chunk.content)
