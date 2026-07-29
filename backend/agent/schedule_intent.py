import json
from datetime import datetime

from croniter import croniter
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, ValidationError

from agent import reasoning


class ScheduleIntentError(RuntimeError):
    """La détection d'intention de planification n'a pas pu produire un
    résultat exploitable (réponse LLM non conforme, cron invalide)."""


class ScheduleIntent(BaseModel):
    """`scheduled=False` signifie : demande immédiate, à traiter comme un
    plan/chat normal (Phase 2), pas comme une automatisation."""

    scheduled: bool = False
    recurring: bool = False
    cron: str | None = None
    name: str | None = None
    task: str | None = None


def _system_prompt(now: datetime) -> str:
    return (
        "Tu analyses un message adressé à Jarvis pour détecter une intention de "
        "planification : l'utilisateur demande-t-il une action PLUS TARD ou de façon "
        'RÉCURRENTE (ex. "dans 2 minutes", "demain à 8h", "tous les matins", "chaque '
        'lundi") plutôt que MAINTENANT ?\n\n'
        f"Il est actuellement {now.strftime('%A %Y-%m-%d %H:%M')} (UTC).\n\n"
        'Réponds UNIQUEMENT avec un objet JSON de la forme {"scheduled": bool, '
        '"recurring": bool, "cron": "..." ou null, "name": "..." ou null, "task": "..." ou null}.\n\n'
        "- Ponctuel (\"dans N minutes/heures\", \"demain à HHhMM\") : scheduled=true, "
        "recurring=false, cron = expression cron UTC à 5 champs pointant la date/heure "
        "précise obtenue en ajoutant le délai à maintenant (ex. minute+heure+jour+mois "
        "exacts, dernier champ *).\n"
        "- Récurrent (\"tous les jours\", \"chaque lundi\", \"toutes les semaines\") : "
        "scheduled=true, recurring=true, cron = motif récurrent standard.\n"
        "- Ni l'un ni l'autre (demande immédiate ou simple conversation) : "
        '{"scheduled": false, "recurring": false, "cron": null, "name": null, "task": null}.\n\n'
        '"task" reformule l\'action demandée SANS l\'indication temporelle (ce sera transmis '
        'tel quel au planificateur de tools). "name" est un nom court pour identifier '
        "l'automatisation. Aucun texte en dehors du JSON, pas de balises de code."
    )


def detect_schedule_intent(goal: str, now: datetime) -> ScheduleIntent:
    """Décide si `goal` décrit une action différée/récurrente. Utilise le même
    mécanisme JSON-mode manuel que agent/planner.py (pas de function-calling,
    plus robuste avec les petits modèles gratuits)."""
    llm = reasoning._get_llm()
    response = llm.invoke([SystemMessage(content=_system_prompt(now)), HumanMessage(content=goal)])
    raw = reasoning.strip_json_code_fence(str(response.content))

    try:
        payload = reasoning.parse_json_object(raw)
        intent = ScheduleIntent.model_validate(payload)
    except (json.JSONDecodeError, ValidationError) as exc:
        raise ScheduleIntentError(f"Réponse non conforme au format attendu : {raw!r}") from exc

    if intent.scheduled and not croniter.is_valid(intent.cron or ""):
        raise ScheduleIntentError(f"Expression cron invalide générée par le LLM : {intent.cron!r}")

    return intent
