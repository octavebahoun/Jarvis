# Backend — Jarvis-like

Backend du projet **Double Numérique Intelligent** basé sur **FastAPI**.

## Objectif

Fournir une API qui orchestre :

- le raisonnement agentique,
- la gestion du profil utilisateur,
- la mémoire court/long terme,
- la recherche sémantique (RAG) via une base vectorielle.

## État actuel (index du projet)

Le dossier backend est **scaffoldé** : l’arborescence est prête, mais la majorité des modules Python sont encore vides.

Fichiers clés déjà présents :

- `main.py` (entrée FastAPI, vide pour l’instant)
- `api/routes/` (routes `chat`, `memory`, `profile`)
- `agent/` (`controller`, `reasoning`)
- `memory/` (`short_term`, `long_term`, `vector_store`)
- `identity/profile.py`
- `db/` (`models`, `session`)

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

## Priorités de développement backend

1. Initialiser `main.py` avec l’app FastAPI et l’enregistrement des routers.
2. Implémenter les endpoints de base :
   - `POST /chat`
   - `GET/POST /memory`
   - `GET/PUT /profile`
3. Créer la couche DB (`db/session.py`, `db/models.py`).
4. Brancher la mémoire vectorielle dans `memory/vector_store.py`.
5. Ajouter observabilité, gestion d’erreurs et tests.

## Convention recommandée

- API REST versionnable (`/api/v1/...`)
- séparation claire : `routes -> services -> storage`
- typage Pydantic strict
- tests unitaires + intégration dès les premiers endpoints
