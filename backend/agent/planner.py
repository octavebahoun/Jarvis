import json

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field, ValidationError

import tools
from agent import reasoning


class PlannerError(RuntimeError):
    """Le planner n'a pas pu produire un plan exploitable (réponse LLM non conforme)."""


class PlannedStep(BaseModel):
    tool: str
    description: str
    args: dict = Field(default_factory=dict)


class ProposedPlan(BaseModel):
    """Un plan à 0 étape signifie : la demande ne nécessite aucun tool,
    à traiter comme du chat normal (Phase 1)."""

    steps: list[PlannedStep] = Field(default_factory=list)


def _tools_catalog() -> str:
    return "\n".join(f"- {tool.name}: {tool.description}" for tool in tools.list_tools())


def _system_prompt() -> str:
    return (
        "Tu es le planificateur de l'agent Jarvis. Voici les tools disponibles :\n\n"
        f"{_tools_catalog()}\n\n"
        'Réponds UNIQUEMENT avec un objet JSON de la forme '
        '{"steps": [{"tool": "...", "description": "...", "args": {...}}]}. '
        "Utilise exclusivement les noms de tools listés ci-dessus. "
        'Si la demande ne nécessite aucun tool (simple question ou conversation), '
        'réponds {"steps": []}. Aucun texte en dehors du JSON, pas de balises de code.'
    )


def _strip_code_fence(text: str) -> str:
    """Certains modèles entourent le JSON de ```json ... ``` malgré la consigne."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else ""
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
    return text.strip()


def build_plan(goal: str) -> ProposedPlan:
    """Décide si `goal` nécessite des tools et, si oui, le découpe en étapes structurées."""
    llm = reasoning._get_llm()
    response = llm.invoke([SystemMessage(content=_system_prompt()), HumanMessage(content=goal)])
    raw = _strip_code_fence(str(response.content))

    try:
        payload = json.loads(raw)
        plan = ProposedPlan.model_validate(payload)
    except (json.JSONDecodeError, ValidationError) as exc:
        raise PlannerError(f"Réponse du planner non conforme au format attendu : {raw!r}") from exc

    known_tool_names = {tool.name for tool in tools.list_tools()}
    for step in plan.steps:
        if step.tool not in known_tool_names:
            raise PlannerError(f"Le planner a référencé un tool inconnu : {step.tool!r}")

    return plan
