# 04 — Executor (exécution d'un plan approuvé)

## Ce qui a été construit

- `agent/executor.py` : `execute_plan(db, plan)`. Refuse d'exécuter un plan
  dont le statut n'est pas `"approved"` (`PlanNotApprovedError`) — c'est la
  garde-fou qui matérialise la validation humaine obligatoire (règle de
  `phase2.md`).
- Exécute les étapes **dans l'ordre**, une à la fois : `tools.get_tool(step.tool).run(**step.args)`.
  Conforme à la règle d'architecture du projet — `executor.py` appelle les
  tools, jamais `controller.py` directement, et un tool n'appelle jamais un
  autre tool.
- **S'arrête à la première étape en échec** : le plan passe en `"failed"`,
  l'étape fautive récupère l'erreur, les étapes suivantes restent `"pending"`
  (jamais tentées). Choix simple et prévisible plutôt qu'une logique de
  retry/skip qui n'a pas été demandée.

## Décision : une seule validation, au niveau du plan entier

`phase2.md` décrit un flux à une seule porte de validation ("plan → validation
utilisateur → exécution étape par étape"), pas une reconfirmation à chaque
étape sensible individuellement. Approuver le plan entier (bloc suivant : API
`/tasks/:id/approve`) vaut donc consentement pour toutes ses étapes, y compris
celles marquées `requires_validation: True` (`code_executor`, futur
`browser_automation`) — le `PlanViewer` (frontend, bloc à venir) devra
afficher clairement les actions sensibles avant cette approbation unique.

## Vérifié

3 tests (`tests/test_executor.py`) : refus si non approuvé, exécution
complète réussie (2 étapes `file_reader`), arrêt à la première échec (fichier
manquant) avec les étapes suivantes intactes. Suite complète : 45 tests.
