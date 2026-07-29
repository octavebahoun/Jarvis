# 02 — Pont chat → automatisation (langage naturel)

## Le problème

Après la première brique de Phase 3 (doc 01), créer une automatisation
exigeait un appel API brut (`POST /automations` avec un cron écrit à la
main) — aucun moyen de dire simplement à Jarvis dans le chat *"cherche les
news IA dans 2 minutes"* ou *"fais ça tous les matins"*. Remarque de
l'utilisateur après validation du socle : *"c'est pas un prompt je lance une
automatisation du genre 'lance une recherche sur l'IA dans 2min' ?"*

## Ce qui a été construit

- **`agent/schedule_intent.py`** (`detect_schedule_intent`) : même mécanisme
  JSON-mode manuel que `agent/planner.py` — demande au LLM si le message
  décrit une action **différée** ou **récurrente** plutôt qu'immédiate. La
  date/heure actuelle (UTC) est injectée dans le prompt pour que le LLM
  puisse calculer une date absolue à partir d'une expression relative
  ("dans 2 minutes" → minute/heure/jour/mois précis dans l'expression cron
  générée). Distingue :
  - **Ponctuel** (`recurring=false`) : cron pointant une date/heure exacte
    (ex. "dans 2 min" → `"32 14 29 7 *"`).
  - **Récurrent** (`recurring=true`) : motif cron classique (ex. "tous les
    matins" → `"0 9 * * *"`).
  - **Ni l'un ni l'autre** : `scheduled=false`, le message est une demande
    immédiate (comportement Phase 2 inchangé).
- **`agent/controller.py`** : `_maybe_create_automation`, appelé **avant**
  `_maybe_create_plan` dans `handle_chat_or_plan`/`stream_chat_or_plan`. Si
  une intention de planification est détectée, l'automatisation est créée
  directement (même chemin que `POST /automations`) et le plan/chat immédiat
  n'est jamais consulté pour ce message. Si la détection échoue (LLM
  indisponible, réponse non conforme), l'exception est absorbée et le flux
  retombe sur le comportement existant (plan puis chat) — même stratégie de
  dégradation gracieuse que le planner.
- **Nouveau type de réponse `"automation"`** sur `/chat` (`ChatResponse`) et
  nouveau marqueur `AUTOMATION_MARKER` sur `/chat/stream`, symétriques à
  `"plan"`/`PLAN_MARKER`.
- **`GET /automations/:id`** (manquant jusqu'ici — seul `GET /automations`
  existait) : nécessaire pour que le frontend affiche l'automatisation
  programmée depuis le chat.
- **Frontend** : `AutomationCard.tsx` (mirroring `PlanViewer.tsx`, sans
  bouton d'approbation — l'automatisation est déjà active) ; `ChatWindow.tsx`
  et `lib/api.ts` étendus pour le nouveau rôle de message `"automation"`.

## Décisions et pourquoi

- **Détection d'intention séparée du planner** (nouveau module plutôt
  qu'étendre `planner.py`) : deux décisions différentes (quand agir vs. quoi
  faire) — le planner reste inchangé, ne décide toujours que des tools, pas
  du timing.
- **Priorité automatisation > plan > chat** : un message qui ressemble à la
  fois à une action différée et à une action outillée (ex. "cherche X dans 2
  min") doit être programmé, pas exécuté tout de suite.
- **Pas de validation humaine à la création** (comme un appel direct à
  `POST /automations`) : créer une automatisation n'est pas une action
  sensible en soi (rien ne s'exécute avant le déclenchement programmé) — le
  garde-fou sécurité existant (doc 01) s'applique de toute façon au moment de
  l'exécution proactive, pas de la création.
- **`_strip_code_fence` factorisé** dans `agent/reasoning.py`
  (`strip_json_code_fence`) plutôt que dupliqué : `planner.py` et
  `schedule_intent.py` partagent maintenant le même helper.

## Limite connue

Une expression relative ("dans 2 minutes") produit une date **exacte**, donc
un cron qui ne matchera plus après ce jour-là — mais l'automatisation reste
`active: true` indéfiniment (elle recommencerait à matcher un an plus tard,
à la même date/heure). Pas de désactivation automatique après une exécution
ponctuelle pour l'instant — acceptable en l'état (l'utilisateur peut
toggle/laisser tel quel), à corriger si ça devient gênant en usage réel.

## Vérifié

Nouveaux tests : `test_schedule_intent.py` (parsing JSON, ponctuel vs
récurrent, cron invalide, JSON invalide), `test_chat_automation_mode.py`
(priorité automatisation > plan, dégradation gracieuse, marqueur de stream,
`GET /automations/:id`). `tests/conftest.py` : le fixture `client` neutralise
désormais aussi `schedule_intent.detect_schedule_intent` par défaut (même
principe que pour `planner.build_plan`), sinon chaque test de chat existant
déclenchait un vrai appel LLM avant d'atteindre le planner mocké.

Suite complète verte (SQLite + Redis simulé via `fakeredis` pour vérifier
spécifiquement ce flux ; échecs restants = tests déjà connus nécessitant un
vrai Redis, absent de ce sandbox). Frontend : `tsc --noEmit`, `npm run lint`,
`npm run build` tous verts.
