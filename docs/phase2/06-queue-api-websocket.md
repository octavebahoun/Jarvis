# 06 — Queue Celery, API tasks, câblage /chat, WebSocket

## Ce qui a été construit

### Câblage controller (`/chat` peut désormais proposer un plan)

- `agent/controller.py` : `handle_chat_or_plan()` (non-streaming) et
  `stream_chat_or_plan()` (streaming) — deux **wrappers** ajoutés autour de
  `handle_chat`/`stream_chat`, qui restent totalement inchangés. Ils
  appellent d'abord `planner.build_plan()` ; si des étapes sont proposées,
  le plan est persisté (statut `pending`) et retourné **sans appeler le LLM
  de chat** ; sinon, comportement Phase 1 intact.
- Le planner tourne sur **chaque** message (détection systématique, conforme
  au flux documenté dans `phase2.md`) — un coût en latence assumé.
- `/chat/stream` (texte brut) signale un plan par un chunk unique :
  `PLAN_MARKER + plan_id`. Le frontend devra détecter ce préfixe et aller
  chercher les détails via `GET /tasks/:id` plutôt que d'afficher ce chunk
  comme du texte de chat.
- `/chat` (JSON) a un champ `type` (`"reply"` | `"plan"`) en plus de `reply`
  — ajout **additif**, les anciens tests Phase 1 qui ne lisaient que `reply`
  continuent de passer sans modification.
- Si le planner échoue (JSON invalide, LLM indisponible...), l'erreur est
  loggée et le contrôleur **retombe sur le chat simple** plutôt que de
  planter la requête — même philosophie que la dégradation gracieuse de la
  mémoire vectorielle (doc 17 de la Phase 1).

### Queue asynchrone (Celery + Redis)

- `tasks/worker.py` : `celery_app` (broker + backend Redis, **DB Redis
  dédiées** — `/1` et `/2` — séparées de celles utilisées par la mémoire
  court terme). La logique métier (`_run_plan`) est séparée de la tâche
  Celery elle-même (`execute_plan_task`) pour rester testable sans broker réel.
- `docker-compose.yml` : nouveau service `worker` (même image que `backend`,
  commande `celery ... worker`), avec le même accès au socket Docker que le
  backend (les tools sandboxés tournent dans le worker, pas dans l'API).

### API

- `GET /tasks/:id` : détails d'un plan (statut, étapes, résultats/erreurs).
- `POST /tasks/:id/approve` : passe le plan en `approved` puis déclenche
  `execute_plan_task.delay(plan_id)` (exécution asynchrone, l'appel HTTP ne
  bloque pas). Refuse (409) un plan qui n'est pas `pending`.
- `api/schemas.py` : `PlanResponse`/`plan_to_response()` partagés entre
  `chat.py`, `tasks.py` et le WebSocket — un seul endroit de sérialisation.

### WebSocket temps réel

- `GET /ws/tasks/:id` (`api/routes/ws_tasks.py`) : pousse l'état du plan
  jusqu'à un statut terminal (`done`/`failed`). Implémenté par **polling DB**
  (1x/seconde) plutôt qu'un vrai pub/sub — l'exécution tourne dans le worker
  Celery, un **processus séparé** de l'API ; relire l'état persisté est la
  façon la plus simple d'observer sa progression entre process.
  `db.expire_all()` avant chaque lecture : sans ça, SQLAlchemy renverrait
  l'état mis en cache par la session plutôt que l'état réel en base, écrit
  par un autre processus.

## Limite connue (assumée pour l'instant)

Le handler WebSocket est `async def` mais utilise une session SQLAlchemy
**synchrone** (bloquante) — chaque poll bloque brièvement la boucle asyncio.
Acceptable pour un MVP mono-utilisateur ; passer à SQLAlchemy async serait un
changement bien plus large, pas demandé ici.

## Vérifié

12 nouveaux tests (`test_chat_plan_mode.py`, `test_tasks_routes.py`,
`test_worker.py`) : `/chat` et `/chat/stream` basculent bien en mode plan
selon la réponse du planner (mocké), dégradation gracieuse si le planner
échoue, `GET/POST /tasks` (Celery `.delay()` mocké — aucun broker réel requis
dans ce sandbox), `_run_plan()` exécute réellement un plan de bout en bout.
Suite complète : 66 tests.

Non vérifié ici : un vrai worker Celery connecté à un vrai Redis, et le
WebSocket avec un vrai navigateur — nécessite Docker + Redis actifs (bloc
suivant : frontend, à tester sur ta machine).
