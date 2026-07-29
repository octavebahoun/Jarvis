# Backend — Jarvis-like

Backend du projet **Double Numérique Intelligent** basé sur **FastAPI**.

## Objectif

Fournir une API qui orchestre :

- le raisonnement agentique,
- la gestion du profil utilisateur,
- la mémoire court/long terme,
- la recherche sémantique (RAG) via une base vectorielle.

## État actuel (index du projet)

La Phase 1 (chat + mémoire + profil) est implémentée :

- `main.py` : app FastAPI, CORS, `init_db()` au démarrage.
- `api/routes/` : `chat.py` (`POST /chat`), `memory.py` (`GET /memory`),
  `profile.py` (`GET/PUT /profile`).
- `agent/` : `controller.py` (orchestration), `reasoning.py` (prompt +
  appel LLM).
- `memory/` : `short_term.py` (Redis), `long_term.py` (faits PostgreSQL),
  `vector_store.py` (Chroma, RAG).
- `identity/profile.py` : profil utilisateur (utilisateur unique en Phase 1).
- `db/` : `models.py` (`User`, `Fact`, `Message`), `session.py` (engine +
  `init_db`).
- `tests/` : suite pytest (`GET /health`, `/profile`, `/chat`, `/memory`) —
  voir la section Tests ci-dessous.

## Stack backend

- Python 3.11
- FastAPI + Uvicorn
- SQLAlchemy + Alembic
- PostgreSQL (données relationnelles)
- Redis (sessions/cache)
- ChromaDB (mémoire vectorielle)
- LangChain + OpenAI (raisonnement/agent)

## Lancement en local (dev)

1. Créer et activer un environnement virtuel Python.
2. Installer les dépendances :
   - `pip install -r requirements.txt`
3. Ajouter les variables d’environnement nécessaires (`.env` à la racine).
4. Démarrer l’API :
   - `uvicorn main:app --host 0.0.0.0 --port 8080 --reload`

## Lancement via Docker

Le backend est prévu pour être lancé avec `docker-compose` depuis la racine du projet.

Le service backend :

- build depuis `./backend`
- écoute sur le port `8080`
- dépend de `postgres`, `redis`, `chroma`

## Tests

```bash
docker-compose up -d postgres redis   # pas besoin de chroma/backend pour les tests
pip install -r requirements-dev.txt
pytest -v
```

Le LLM et la mémoire vectorielle sont simulés (voir `tests/conftest.py`) : pas
besoin de clé `OPENAI_API_KEY` ni de service Chroma actif pour lancer la suite.

## Migrations (Alembic)

Le schéma est géré par Alembic (`alembic/`), pas par `create_all()` seul —
nécessaire dès qu'une table existante change (ex. `Plan.summary`, Phase 2) :
`create_all()` crée les tables manquantes mais n'altère jamais une table déjà
présente. `docker-compose` applique les migrations automatiquement au
démarrage (`backend` et `worker`, cf. `dockerfile`/`docker-compose.yml`).

```bash
# Après tout changement de backend/db/models.py :
alembic revision --autogenerate -m "description du changement"
alembic upgrade head
```

`alembic/env.py` lit `DATABASE_URL` depuis `config.get_settings()` (donc
depuis l'environnement), pas depuis une valeur figée dans `alembic.ini`.

## Prochaines priorités (au-delà des Phases 1 et 2)

1. Ajouter observabilité (logs structurés) et gestion d’erreurs sur les
   appels LLM (timeout / erreur API OpenAI → réponse dégradée plutôt que 500)
   — fait pour le chat (Phase 1), à généraliser.
2. Authentification (JWT) quand le multi-utilisateur devient nécessaire.

## Convention recommandée

- API REST versionnable (`/api/v1/...`)
- séparation claire : `routes -> services -> storage`
- typage Pydantic strict
- tests unitaires + intégration dès les premiers endpoints
