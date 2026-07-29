# Résumé de session — pour reprise dans une nouvelle discussion

## Projet

**Jarvis** (`octavebahoun/Jarvis`, branche `claude/projet-anonyme-ch2wyx`) —
agent IA personnel. Stack : FastAPI (backend), Next.js (frontend),
PostgreSQL + Redis + ChromaDB, LangChain, Docker Compose.

## Contrainte impérative

**Aucune trace de Claude dans le repo.** Commits signés au nom de
l'utilisateur (`Octave BAHOUN-HOUTOUKPE <octavebahoun@gmail.com>`), jamais de
mention Claude/Anthropic dans le code, les commits ou la doc. Un incident a
eu lieu (commits signés "Claude" par défaut par l'environnement) — corrigé
par réécriture d'historique (`git filter-branch`) + `git config` local.

## Convention de travail établie

- **Un commit par évolution logique**, message en français, jamais de
  co-auteur/footer.
- **Chaque évolution est documentée** dans `docs/phase1/NN-*.md` ou
  `docs/phase2/NN-*.md` (séquentiel, avec sommaire dans le `README.md` de
  chaque dossier) : ce qui a été construit, les décisions et pourquoi, ce qui
  a été vérifié.
- **Tout est testé avant de committer** : suite `pytest` (backend) +
  `tsc --noEmit`/`npm run lint`/`npm run build` (frontend) + vérification
  réelle en navigateur (Playwright, screenshots) quand pertinent.
- Ce sandbox n'a **pas de daemon Docker actif** ni accès à un vrai
  Postgres/Redis/Chroma en continu : tout a été testé avec des substituts
  (SQLite, `fakeredis`, client Docker simulé) — d'où plusieurs bugs
  découverts seulement lors des tests réels de l'utilisateur sur sa machine
  (voir plus bas).
- Script réutilisable pour lancer les tests backend dans ce sandbox :
  `/tmp/claude-0/.../scratchpad/run_backend_tests_locally.sh` (substitue
  Postgres→SQLite, Redis→fakeredis, restaure `conftest.py` après coup).

## Phase 1 — Terminée (chat + mémoire + profil)

- Chat FastAPI (`/chat` JSON, `/chat/stream` streaming texte brut).
- Mémoire court terme (Redis, TTL 2h), long terme (facts PostgreSQL),
  vectorielle (Chroma, RAG) — provider configurable
  (`EMBEDDING_PROVIDER=openai|local`, local = MiniLM ONNX embarqué dans
  Chroma, gratuit).
- LLM configurable (`CHAT_PROVIDER=openai|openrouter`, OpenRouter = modèles
  `:free` gratuits).
- Frontend `/chat` : streaming, indicateur "Jarvis réfléchit", persistance de
  session (localStorage + rehydratation), erreurs différenciées (réseau/422/
  LLM), panneau Profil & mémoire long terme (lecture seule), rendu markdown +
  horodatage des messages.
- Dégradation gracieuse : panne LLM → 502 propre (chat) / marqueur dans le
  flux (stream) ; panne mémoire vectorielle → chat continue sans RAG.
- Suite pytest dédiée (`requirements-dev.txt`).

## Phase 2 — Terminée (agent, tools, plans), en cours de validation réelle

- **Tool System** : `BaseTool` + registre statique (`tools/__init__.py`).
  Tools : `file_reader` (lecture seule, confiné à `SANDBOX_PATH`),
  `web_search` (API Tavily), `code_executor` (Python sandboxé Docker, réseau
  désactivé, `requires_validation`), `browser_automation` (Playwright,
  image officielle, réseau activé, `requires_validation`).
- **Planner** (`agent/planner.py`) : décide via le LLM (JSON-mode manuel, pas
  de function-calling — plus robuste avec les petits modèles gratuits) si
  une demande nécessite des tools ; 0 étape = chat normal inchangé.
- **Executor** (`agent/executor.py`) : exécute un plan **approuvé**, étape
  par étape, s'arrête à la première erreur. Une fois toutes les étapes
  réussies, génère une **synthèse finale en langage naturel**
  (`Plan.summary`) à partir des résultats — dégrade proprement si la synthèse
  échoue (plan quand même "done").
- **Persistance** : modèles `Plan`/`PlanStep` (PostgreSQL), CRUD dans
  `tasks/task_store.py`.
- **Queue asynchrone** : Celery + Redis (DB dédiées `/1` `/2`), worker séparé
  (`docker-compose.yml` : service `worker`).
- **API** : `POST /chat` et `/chat/stream` détectent et proposent un plan
  (wrappers `handle_chat_or_plan`/`stream_chat_or_plan`, le comportement
  Phase 1 `handle_chat`/`stream_chat` reste inchangé) ; `GET /tasks/:id`,
  `POST /tasks/:id/approve` ; WebSocket `/ws/tasks/:id` (polling DB, le
  worker tourne dans un process séparé).
- **Frontend** : `PlanViewer`/`ToolCallCard`/`TaskStatus`, rendu inline dans
  le fil de chat, cycle complet pending → approbation → suivi temps réel →
  résultat + synthèse.
- **Sécurité** : sandboxes Docker jetables (timeout strict, suppression
  garantie), confinement fichier, validation humaine obligatoire sur les
  tools sensibles.
- 69 tests pytest (tout mocké : LLM, Docker, Celery `.delay()`).

## Bugs trouvés en test réel (sur la machine de l'utilisateur, Docker) et corrigés

Ce sandbox n'ayant pas de vrai Docker/Postgres/Redis en continu, ces bugs
n'étaient détectables qu'en conditions réelles :

1. **Réseau Docker Compose** : `.env` utilisait `localhost` pour
   DB/Redis/Chroma/Celery — invalide depuis l'intérieur d'un container.
   Fixé via `environment:` dans `docker-compose.yml` (surcharge avec les noms
   de service).
2. **Imports différés dans le worker Celery** : `tasks/worker.py` importait
   `agent.executor` etc. à l'intérieur de la fonction plutôt qu'en haut du
   module — cassait au moment de l'exécution réelle d'une tâche (Celery
   n'ajoute `/app` à `sys.path` que temporairement au chargement de l'app).
   Fixé : imports remontés en tête de module.
3. **Image Docker non téléchargée** : `client.containers.create()` (API bas
   niveau) ne pull pas une image manquante, contrairement à `docker run`.
   Fixé : `_ensure_image()` dans `tools/_sandbox.py`.
4. **`create_all()` n'altère jamais une table existante** : l'ajout de
   `Plan.summary` n'a jamais été appliqué à la base Postgres déjà créée.
   Fixé : mise en place complète d'**Alembic** (migration baseline générée
   et vérifiée, `docker-compose`/`dockerfile` appliquent `alembic upgrade
   head` au démarrage de `backend` et `worker`).
5. Docker-compose ne montait pas `SANDBOX_PATH` (`file_reader` invisible aux
   fichiers déposés par l'utilisateur) — fixé (volume `./sandbox:/app/sandbox`).

## État actuel / à faire au prochain tour

- L'utilisateur vient de relancer avec `docker compose down -v` +
  `up -d --build` après le fix Alembic (colonne `summary` manquante) — **son
  retour de test n'est pas encore arrivé** au moment de ce résumé.
- Tests fonctionnels déjà confirmés en réel : `web_search` (Tavily) ✅,
  `file_reader` ✅ (après fix imports Celery). `code_executor` et la synthèse
  finale restent à reconfirmer après le dernier fix (Alembic).
- Checklist de test manuel complète disponible :
  `docs/checklist-test-manuel.md`.
- Décision actée : on reste sur la branche unique
  `claude/projet-anonyme-ch2wyx` pour l'instant ; les phases suivantes (3, 4)
  partiront sur des branches séparées le moment venu.
- Idée mise en attente (pas commencée) : donner une voix à Jarvis (TTS/STT) —
  prévu Phase 4 dans la roadmap du projet, discuté mais explicitement
  reporté par l'utilisateur.
- Prochaine étape naturelle une fois la Phase 2 validée à 100% en réel :
  Phase 3 (automatisation, dashboard) — pas encore entamée, pas encore
  présentée en détail.

## Fichiers clés pour se repérer rapidement

- `phase1.md`, `phase2.md`, `phase3.md`, `phase4.md`, `prérequis.md`,
  `architecture.md`, `cour.md` — specs et roadmap d'origine du projet.
- `docs/phase1/`, `docs/phase2/` — journal détaillé de chaque évolution
  (à lire dans l'ordre indiqué par leurs `README.md`).
- `docs/checklist-test-manuel.md` — tests fonctionnels à faire à la main.
