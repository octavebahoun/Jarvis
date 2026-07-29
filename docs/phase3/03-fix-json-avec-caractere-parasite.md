# 03 — Fix : JSON du LLM avec caractère parasite en fin de réponse

## Le problème (découvert en test réel, automatisation ponctuelle)

Après validation du pont chat → automatisation (doc 02), la première
automatisation ponctuelle réellement déclenchée par Celery Beat échoue :

```
json.decoder.JSONDecodeError: Extra data: line 1 column 176 (char 175)
agent.planner.PlannerError: Réponse du planner non conforme au format
attendu : '{"steps": [{"tool": "web_search", ...}]}]'
```

Le modèle gratuit (OpenRouter `:free`) a renvoyé un JSON par ailleurs
parfaitement valide, mais suivi d'un `]` en trop. `json.loads()` rejette
tout le bloc dès qu'il reste du texte après la valeur JSON — le plan entier
est perdu alors que son contenu était exploitable.

## Cause

`planner.py` et `schedule_intent.py` utilisaient tous les deux `json.loads`
directement. `strip_json_code_fence` gère déjà le cas des balises
` ```json ` autour de la réponse, mais pas celui d'un fragment parasite
*après* un JSON valide — un mode d'échec différent, plus fréquent avec les
petits modèles gratuits que les gros modèles payants.

## Correctif

Nouveau helper **`agent/reasoning.py::parse_json_object`** : utilise
`json.JSONDecoder().raw_decode()` plutôt que `json.loads()` — parse le
premier objet JSON valide en tête du texte et ignore tout ce qui suit,
plutôt que de rejeter le tout. `planner.py` et `schedule_intent.py`
l'utilisent désormais tous les deux (après `strip_json_code_fence`, qui
retire l'espace/les balises en tête — `raw_decode` n'accepte pas d'espace
avant le JSON, contrairement à `json.loads`).

## Vérifié

Nouveaux tests : `test_reasoning.py` (JSON propre, JSON avec caractère
parasite, JSON invalide — toujours une `JSONDecodeError`, comportement
inchangé pour les appelants), `test_planner.py` et `test_schedule_intent.py`
(cas concret rencontré : crochet fermant en trop). Suite complète (79 tests
hors ceux nécessitant un vrai Redis, absent de ce sandbox) verte.
