# 12 — Synthèse finale du plan (réponse en langage naturel)

## Le problème signalé

Après le fix du worker (doc 10), un premier vrai test *"Lis le fichier
octave.txt et résume-le"* a bien lu le fichier (`file_reader` fonctionnait),
mais l'utilisateur n'a reçu que le **contenu brut** en guise de "résumé" —
aucune vraie synthèse. Cause : le plan Phase 2 n'avait aucune étape de
synthèse finale ; `execute_plan` se contentait d'exécuter les tools et
d'afficher leurs résultats bruts dans les `ToolCallCard`, sans jamais
redonner la main au LLM pour formuler une réponse.

## Ce qui a été construit

- `db.models.Plan.summary` (Text, nullable) : synthèse en langage naturel,
  `None` tant qu'elle n'a pas été générée ou si elle a échoué.
- `tasks.task_store.set_plan_summary()`.
- `agent/executor.py` : une fois **toutes** les étapes réussies (avant de
  passer le plan à `"done"`), `_build_summary_prompt()` construit un prompt à
  partir de l'objectif initial (`plan.goal`) et des résultats de chaque étape,
  puis `reasoning.generate_reply()` (même sélecteur OpenAI/OpenRouter que le
  chat normal, doc 14 de la Phase 1) produit la synthèse.
- **Dégradation gracieuse** : si la synthèse échoue (LLM indisponible...),
  l'erreur est loggée mais le plan passe quand même à `"done"` avec
  `summary = None` — les résultats bruts par étape restent affichés dans tous
  les cas, même philosophie que la mémoire vectorielle (Phase 1, doc 17).
- `api/schemas.py` : `PlanResponse.summary` (ajout additif).
- Frontend (`PlanViewer.tsx`) : la synthèse s'affiche en markdown sous les
  `ToolCallCard`, une fois présente.

## Décision : pas de synthèse si une étape échoue

Si le plan passe à `"failed"`, aucune synthèse n'est tentée — l'erreur brute
de l'étape fautive (déjà visible dans son `ToolCallCard`) suffit à expliquer
ce qui s'est passé ; ajouter une synthèse sur un échec n'a pas été demandé et
aurait ajouté de la complexité (que dire d'un échec partiel ?) sans besoin
exprimé.

## Vérifié

4 tests (`test_executor.py`) : synthèse générée à partir des résultats,
synthèse absente mais plan quand même `"done"` si le LLM échoue. `tsc`/`lint`
propres. Test réel en navigateur (backend simulé, LLM mocké) : la synthèse
markdown s'affiche correctement, séparée du résultat brut de l'étape. Suite
complète : 69 tests.
