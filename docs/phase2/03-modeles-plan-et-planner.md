# 03 — Modèles Plan/PlanStep + planner (décision LLM)

## Ce qui a été construit

- `db/models.py` : `Plan` (objectif, statut `pending → approved → running →
  done|failed`, session/utilisateur) et `PlanStep` (tool, description, args,
  statut, résultat/erreur, ordre). Un plan est persisté **avant** toute
  exécution (règle explicite de `phase2.md` : traçabilité).
- `tasks/task_store.py` : CRUD pur (`create_plan`, `get_plan`,
  `set_plan_status`, `set_step_result`) — aucune logique LLM, aucun appel de
  tool. Emplacement conforme à l'arborescence documentée dans `phase2.md`.
- `agent/planner.py` : `build_plan(goal) -> ProposedPlan`. Décide si la
  demande nécessite des tools et, si oui, la découpe en étapes. **Aucun accès
  DB** ici — persister le plan est la responsabilité de `task_store`, pas du
  planner (même séparation stricte que memory/identity/agent en Phase 1).

## Décision : JSON-mode manuel plutôt que `with_structured_output`

LangChain propose `llm.with_structured_output(...)`, mais ça repose sur le
function-calling natif du modèle — peu fiable avec des petits modèles gratuits
(`CHAT_PROVIDER=openrouter`, cf. doc 14 de la Phase 1), déjà source d'échecs
observés en usage réel. `planner.py` demande donc explicitement au LLM de
répondre en JSON brut (prompt + `json.loads` + validation Pydantic), une
méthode qui fonctionne avec n'importe quel modèle conversationnel, y compris
les plus modestes. Un fallback strip les balises ` ```json ` que certains
modèles ajoutent malgré la consigne.

Sécurité supplémentaire : chaque `tool` référencé dans le plan est vérifié
contre le registre réel (`tools.list_tools()`) — un nom halluciné par le LLM
fait échouer `build_plan` (`PlannerError`) plutôt que de passer silencieusement.

## Convention

**Un plan à 0 étape signifie "traiter comme du chat normal"** — c'est ce
signal que `controller.py` utilisera (prochain bloc) pour décider d'basculer
en mode agent ou de garder le comportement Phase 1 inchangé.

## Vérifié

9 tests (`test_task_store.py`, `test_planner.py`) : persistance des étapes
dans l'ordre, mise à jour de statut, plan vide, plan avec étapes, JSON entouré
de balises markdown, JSON invalide, tool inconnu. LLM entièrement simulé (pas
d'appel réseau). Suite complète : 42 tests.
