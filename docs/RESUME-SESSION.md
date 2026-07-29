# Résumé de session — pour reprise dans une nouvelle discussion

## Projet

**Jarvis** (`octavebahoun/Jarvis`) — agent IA personnel. Stack : FastAPI
(backend), Next.js (frontend), PostgreSQL + Redis + ChromaDB, LangChain,
Docker Compose. Toutes les phases validées à ce jour sont fusionnées dans
`main`. **Un merge est en attente** (voir "État actuel" plus bas).

## Contrainte impérative

**Aucune trace de Claude dans le repo.** Commits signés au nom de
l'utilisateur (`Octave BAHOUN-HOUTOUKPE <octavebahoun@gmail.com>`), jamais de
mention Claude/Anthropic dans le code, les commits ou la doc. Un incident a
eu lieu en tout début de projet (commits signés "Claude" par défaut par
l'environnement) — corrigé par réécriture d'historique + `git config` local.
**Vérifier `git config user.name`/`user.email` en tout début de session** :
l'environnement les réinitialise parfois à "Claude" par défaut à chaque
nouvelle session — à corriger avant le premier commit.

## Convention de travail établie

- **Nouvelle règle (actée par l'utilisateur pendant cette session) :** toute
  nouvelle branche doit suivre la forme `feat/phase...` (ex.
  `feat/phase3-scheduler-automatisations`). Les anciennes branches `claude/*`
  sont abandonnées.
- **C'est l'utilisateur qui merge lui-même** les branches dans `main` (via
  les PR GitHub) — ne pas le faire à sa place, ne pas créer de PR sauf
  demande explicite.
- Pousser sur une branche déjà existante plutôt que d'en recréer une à
  chaque évolution si le sujet est le même (ex. les 3 commits Phase 3 de
  cette session sont tous sur la même branche
  `feat/phase3-scheduler-automatisations`).
- **Un commit par évolution logique**, message en français, jamais de
  co-auteur/footer.
- **Chaque évolution est documentée** dans `docs/phase1/NN-*.md`,
  `docs/phase2/NN-*.md` ou `docs/phase3/NN-*.md` (séquentiel, avec sommaire
  dans le `README.md` de chaque dossier) : ce qui a été construit, les
  décisions et pourquoi, ce qui a été vérifié.
- **Tout est testé avant de committer** : suite `pytest` (backend) +
  `tsc --noEmit`/`npm run lint`/`npm run build` (frontend) + vérification
  réelle en navigateur quand pertinent.
- Ce sandbox n'a **pas de vrai Postgres/Chroma en continu**, et **la
  politique réseau de la session bloque le téléchargement d'images Docker**
  (403 côté proxy sur le registre Docker Hub, confirmé via
  `curl $HTTPS_PROXY/__agentproxy/status` — consigne explicite : ne pas
  contourner un refus de politique). Le daemon Docker lui-même **peut** être
  démarré (`dockerd &`, binaire présent, droits root) mais reste inutilisable
  sans images. Tout est donc testé avec des substituts : SQLite (au lieu de
  Postgres), `fakeredis` ou un vrai `redis-server` local (le binaire est
  présent), LLM mocké (pas de clé API réelle disponible ici) — d'où plusieurs
  bugs découverts seulement lors des tests réels de l'utilisateur sur sa
  machine (voir plus bas).
- Pour lancer la suite pytest dans ce sandbox : créer un venv, `pip install
  -r requirements.txt -r requirements-dev.txt`, puis exporter
  `DATABASE_URL=sqlite:////tmp/xxx.db` avant `pytest`. Les tests qui passent
  par le fixture `client` (TestClient FastAPI) ont aussi besoin d'un vrai
  Redis pour les routes `/chat`/`/chat/stream`/`/memory` — sinon ils échouent
  avec `ConnectionRefusedError` (pas un bug : juste l'absence de Redis dans
  ce sandbox). `fakeredis` (`pip install fakeredis`, puis monkeypatcher
  `memory.short_term.get_client`) permet de les vérifier quand nécessaire.

## Phase 1 — Terminée (chat + mémoire + profil), validée en réel

Chat FastAPI (JSON + streaming), mémoire court terme (Redis)/long terme
(Postgres)/vectorielle (Chroma, RAG), LLM et embeddings configurables
(OpenAI ou gratuit), frontend complet (streaming, persistance session,
erreurs différenciées, panneau profil). Détails : `docs/phase1/`.

## Phase 2 — Terminée (agent, tools, plans), validée à 100% en réel

- **Tool System** (`tools/`) : `file_reader` (lecture seule, confiné à
  `SANDBOX_PATH`), `web_search` (Tavily), `code_executor` (Python sandboxé
  Docker, réseau désactivé, `requires_validation`), `browser_automation`
  (Playwright, container dédié, réseau activé, `requires_validation`).
- **Planner** (`agent/planner.py`) : décide via le LLM (JSON-mode manuel, pas
  de function-calling — plus robuste avec les petits modèles gratuits) si
  une demande nécessite des tools.
- **Executor** (`agent/executor.py`) : exécute un plan **approuvé** étape par
  étape, génère une synthèse finale en langage naturel une fois terminé.
- **Queue asynchrone** Celery + Redis, worker séparé. API `/chat` propose des
  plans, `GET/POST /tasks/:id`, WebSocket de suivi temps réel. Frontend
  `PlanViewer`/`ToolCallCard`/`TaskStatus`.
- Checklist de validation manuelle intégralement cochée par l'utilisateur
  (`docs/checklist-test-manuel.md`, section Phase 2).

## Phase 3 — En cours (automatisations proactives)

Trois évolutions poussées cette session sur la branche
`feat/phase3-scheduler-automatisations` (voir "État actuel" — **pas encore
toutes mergées**) :

**1. Socle scheduler + automatisations** (`docs/phase3/01-*.md`)
- Modèle `Automation` (nom, `schedule` cron, `task` en langage naturel,
  `active`, `last_run_at/status/plan_id`).
- `agent/proactive.py::run_automation` : réutilise **le même planner et le
  même executor** que le chat (Phase 2) — transmet `task` à
  `planner.build_plan`, auto-approuve, exécute. **Garde-fou sécurité** :
  bloque et journalise en échec toute étape dont le tool a
  `requires_validation=True` (`code_executor`, `browser_automation`) —
  jamais d'auto-approbation d'une action sensible sans humain.
- `scheduler/registry.py` + `scheduler/jobs.py` : Celery Beat déclenche un
  tick générique chaque minute (`scheduler.tick`), qui cherche les
  automatisations dues via `croniter.match` et délègue à `proactive.py`.
  Nouveau service Docker `beat`.
- API : `POST/GET /automations`, `PUT /automations/:id/toggle`.

**2. Pont chat → automatisation en langage naturel** (`docs/phase3/02-*.md`)
- Idée venue de l'utilisateur : pouvoir écrire *"cherche X dans 2 minutes"*
  ou *"tous les matins"* directement dans le chat, plutôt que d'appeler
  l'API à la main.
- `agent/schedule_intent.py::detect_schedule_intent` : même mécanisme
  JSON-mode que le planner ; détecte une intention différée/récurrente et
  produit un cron (la date/heure UTC courante est injectée dans le prompt
  pour que le LLM calcule une date absolue à partir d'une expression
  relative).
- `controller.py` : `_maybe_create_automation` appelé **avant**
  `_maybe_create_plan` — priorité automatisation > plan immédiat > chat
  simple. Nouveau type de réponse `"automation"` (+ `AUTOMATION_MARKER` en
  streaming), nouvelle route `GET /automations/:id`, composant frontend
  `AutomationCard.tsx`.
- **Validé en réel** par l'utilisateur (Bénin, UTC+1) : le calcul de date
  relative du LLM était correct (attention : à froid, il est facile de se
  tromper de fuseau en relisant les logs — vérifier le fuseau réel de
  l'utilisateur avant de diagnostiquer un "bug" d'heure).

**3. Fix : JSON du LLM avec caractère parasite** (`docs/phase3/03-*.md`)
- Bug réel rencontré : le modèle gratuit OpenRouter a renvoyé un JSON valide
  suivi d'un `]` en trop (`{"steps": [...]}]`) → `json.loads` rejetait tout
  le bloc → automatisation en échec (rattrapé proprement par le garde-fou
  d'erreur de `proactive.py`, mais résultat perdu).
- Fix : `agent/reasoning.py::parse_json_object` (nouveau helper commun,
  utilisé par `planner.py` et `schedule_intent.py`) — `json.JSONDecoder().
  raw_decode()` au lieu de `json.loads()`, parse le JSON valide en tête et
  ignore le surplus.

**Volontairement pas commencé** : intégrations externes GitHub/Notion/
Calendar (OAuth), dashboard frontend (`/dashboard`, mémoire, historique),
désactivation automatique d'une automatisation ponctuelle après son
exécution (actuellement elle reste `active: true` indéfiniment).

## Bugs trouvés en test réel et corrigés (chronologique)

Ce sandbox n'ayant pas de vrai Docker/Postgres/Redis/clé LLM en continu, ces
bugs n'étaient détectables qu'en conditions réelles sur la machine de
l'utilisateur :

1. **Réseau Docker Compose** : `.env` utilisait `localhost` pour
   DB/Redis/Chroma/Celery — invalide depuis l'intérieur d'un container. Fixé
   via `environment:` dans `docker-compose.yml`.
2. **Imports différés dans le worker Celery** cassaient l'exécution réelle
   d'une tâche — imports remontés en tête de module.
3. **Image Docker non téléchargée** : `client.containers.create()` (API bas
   niveau) ne pull pas une image manquante — fixé (`_ensure_image()`).
4. **`create_all()` n'altère jamais une table existante** (colonne
   `Plan.summary` jamais ajoutée à une base déjà créée) — Alembic mis en
   place.
5. **Course entre migrations concurrentes** : `backend` et `worker`
   lançaient chacun `alembic upgrade head` au démarrage — sur une base
   neuve, les deux tentaient de créer la table `alembic_version` en même
   temps (`UniqueViolation`). Fixé : service `migrate` dédié, exécuté une
   seule fois (`depends_on: condition: service_completed_successfully`),
   `postgres` a désormais un `healthcheck`.
6. **Image Playwright officielle sans le paquet pip `playwright`** :
   `mcr.microsoft.com/playwright/python` fournit les navigateurs mais pas le
   paquet Python lui-même → `ModuleNotFoundError`. Fixé : image maison
   (`docker/playwright-sandbox.dockerfile`, service build-only
   `browser-sandbox-image`).
7. **JSON du LLM avec caractère parasite** (détaillé ci-dessus, Phase 3).

## État actuel / à faire au prochain tour

- **⚠️ Priorité : un commit n'est pas encore mergé dans `main`.**
  L'utilisateur a mergé les PR #3 (fix Playwright) et #4 (socle scheduler +
  pont chat) via GitHub, mais le fix JSON (`150c3af "Fix planner/
  schedule_intent : tolère un caractère parasite..."`, poussé après ces
  merges) est resté sur `feat/phase3-scheduler-automatisations` et attend un
  merge dans `main`. Vérifier avec
  `git merge-base --is-ancestor <sha du dernier commit de cette branche> origin/main`
  avant de continuer — ne pas repartir de `main` en pensant que tout y est.
- **Branches obsolètes à nettoyer** (entièrement fusionnées, sans risque,
  mais inutiles) : `feat/phase1`, `feat/phase2` (anciens instantanés
  renommés), et une fois le point ci-dessus réglé,
  `feat/phase2-fix-image-playwright` et
  `feat/phase3-scheduler-automatisations`. Suppression **locale** OK
  (`git branch -d`) ; la suppression **distante** (`git push origin
  --delete`) est refusée par le proxy git de ce sandbox (403) — c'est à
  l'utilisateur de le faire sur GitHub.
- **Automatisation de test résiduelle** créée pendant les essais manuels
  (curl) — l'utilisateur sait la désactiver via
  `PUT /automations/:id/toggle`, mais vérifier qu'il n'en reste pas qui
  tournent pour rien (`GET /automations`).
- **Checklist Phase 3** (`docs/checklist-test-manuel.md`, sections
  "Scheduler + automatisations" et "Pont chat → automatisation") : pas
  encore intégralement cochée par l'utilisateur — notamment le garde-fou
  sécurité (tool sensible bloqué en exécution proactive) et les cas
  d'automatisation récurrente (pas seulement ponctuelle) restent à
  reconfirmer en réel.
- **Idée non commencée, en attente d'arbitrage** : désactiver automatiquement
  une automatisation ponctuelle après sa première exécution réussie (`recurring
  =false` côté `ScheduleIntent`, non exploité pour l'instant côté
  `automation_store`/`proactive.py`).
- **Prochaine étape naturelle de Phase 3**, pas encore entamée : soit les
  intégrations externes (GitHub/Notion/Calendar, nécessitent OAuth), soit le
  dashboard (`/dashboard`, mémoire, historique) — à décider avec
  l'utilisateur.
- Idée mise en attente depuis longtemps (pas commencée) : voix pour Jarvis
  (TTS/STT), prévu Phase 4, explicitement reporté par l'utilisateur.
- Question ouverte de l'utilisateur, pas tranchée : est-ce que travailler
  depuis "Cowork" donnerait accès à son vrai Docker/Internet non filtré (donc
  permettrait de vraiment tester ici plutôt que sur sa machine) — pas de
  réponse certaine apportée, à creuser si le sujet revient.

## Fichiers clés pour se repérer rapidement

- `phase1.md`, `phase2.md`, `phase3.md`, `phase4.md`, `prérequis.md`,
  `architecture.md`, `cour.md` — specs et roadmap d'origine du projet.
- `docs/phase1/`, `docs/phase2/`, `docs/phase3/` — journal détaillé de
  chaque évolution (à lire dans l'ordre indiqué par leurs `README.md`).
- `docs/checklist-test-manuel.md` — tests fonctionnels à faire à la main.
