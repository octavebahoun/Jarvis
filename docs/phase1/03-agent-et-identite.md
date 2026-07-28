# 03 — Identity Core et agent (raisonnement + orchestration)

## Ce qui a été construit

- `backend/identity/profile.py` : `get_or_create_user()` (charge le profil par
  défaut ou le crée à la première requête) et `update_user()` (met à jour stack
  technique / préférences).
- `backend/agent/reasoning.py` : construit le prompt enrichi
  (`build_messages`) à partir du profil, de l'historique court terme et des
  souvenirs pertinents retrouvés dans le vector store, puis appelle le LLM
  (`ChatOpenAI`, modèle configurable via `OPENAI_MODEL`, défaut `gpt-4o`) via
  `generate_reply`.
- `backend/agent/controller.py` : point d'entrée unique de l'agent
  (`handle_chat`). Il orchestre, dans l'ordre :
  1. chargement du profil utilisateur,
  2. récupération de l'historique court terme (Redis),
  3. recherche sémantique dans la mémoire vectorielle,
  4. construction du prompt + appel LLM,
  5. sauvegarde du nouvel échange (Redis pour le court terme, PostgreSQL pour
     l'audit, Chroma pour la recherche sémantique future).

## Décisions

- **Toute la logique métier reste dans `controller.py`**, conformément à la
  règle d'architecture du projet ("logique métier uniquement dans
  `controller.py`", `architecture.md`) : les routes API (doc 04) ne font
  qu'appeler `handle_chat`, aucune logique IA n'y est mêlée.
- **Un seul appel LLM par message**, pas de boucle d'agent (ReAct / tool
  calling). C'est cohérent avec le hors-scope explicite de la Phase 1 : "Agents
  autonomes", "Exécution d'actions système" arrivent en Phase 2.

## État

Le flux complet `POST /chat` → profil → mémoire → LLM → sauvegarde a été
vérifié par un test bout-en-bout (voir doc 04), avec le LLM simulé (pas de vraie
clé OpenAI disponible dans ce sandbox).
