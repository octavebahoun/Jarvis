# 01 — Configuration et base de données

## Ce qui a été construit

- `backend/config.py` : classe `Settings` (pydantic-settings) qui centralise toutes
  les variables d'environnement (`OPENAI_API_KEY`, `DATABASE_URL`, `REDIS_URL`,
  `CHROMA_HOST/PORT`, `SECRET_KEY`, TTL de la mémoire court terme...). Exposée via
  `get_settings()` (mise en cache avec `lru_cache`) pour être injectée partout
  sans relire `.env` à chaque appel.
- `backend/db/session.py` : moteur SQLAlchemy (`engine`), fabrique de sessions
  (`SessionLocal`), classe de base déclarative (`Base`), et `init_db()` qui crée
  les tables manquantes au démarrage de l'API.
- `backend/db/models.py` : trois tables —
  - `User` : profil utilisateur (Identity Core), stack technique et préférences en JSON.
  - `Fact` : mémoire long terme (informations durables sur l'utilisateur).
  - `Message` : journal de conversation persistant (audit, et base pour réindexer
    la mémoire vectorielle si besoin).
- `backend/api/deps.py` : dépendance FastAPI `get_db()` qui ouvre/ferme une
  session SQLAlchemy par requête.

## Décisions

- **Utilisateur unique pour la Phase 1.** Le README de la Phase 1 décrit un seul
  profil (`GET /profile` renvoie directement un profil, sans authentification).
  On charge/crée donc un `User` par défaut (`default_user_id` dans la config)
  plutôt que d'implémenter l'auth JWT tout de suite : `prérequis.md` classe
  explicitement "JWT + sécurité" en priorité Phase 2. L'authentification multi-
  utilisateurs arrivera avec les Tools/Actions de la Phase 2, quand le
  multi-utilisateur aura un sens fonctionnel.
- **`create_all()` plutôt qu'Alembic pour l'instant.** Alembic est dans les
  dépendances et sera introduit dès qu'on aura une première migration réelle à
  versionner (évolution de schéma) ; le générer maintenant pour un schéma qui va
  encore bouger aurait été de la sur-ingénierie.

## État

Le schéma se crée automatiquement au démarrage de l'API (`lifespan` dans
`main.py`, voir doc 04). Testé avec SQLite en local (sandbox sans Docker) et
compatible PostgreSQL tel que configuré dans `docker-compose.yml`.
