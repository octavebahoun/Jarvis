# 06 — Tests backend

## Ce qui a été construit

- `backend/tests/conftest.py` : fixture `client` (FastAPI `TestClient`) et
  fixture `session_id` (identifiant unique par test).
- `backend/tests/test_health.py`, `test_profile.py`, `test_chat.py`,
  `test_memory.py` : couvrent `/health`, `GET/PUT /profile`, `POST /chat`
  (réponse + persistance dans l'historique court terme) et `GET /memory`
  (court et long terme).
- `backend/requirements-dev.txt` (`-r requirements.txt` + `pytest`) et
  `backend/pytest.ini` (`testpaths = tests`).

## Comment les lancer en local

Ces tests sont écrits pour tourner contre de vrais PostgreSQL et Redis (les
mêmes que `docker-compose.yml`), pas contre des services simulés : ça reste
la façon la plus fidèle de vérifier que l'API se comporte comme en production.

```bash
docker-compose up -d postgres redis   # pas besoin de chroma/backend pour les tests
cd backend
pip install -r requirements-dev.txt
pytest -v
```

Le LLM (`agent.reasoning.generate_reply`) et la mémoire vectorielle
(`memory.vector_store`) sont simulés via `monkeypatch` dans `conftest.py` :
les tests n'ont donc pas besoin d'une clé `OPENAI_API_KEY` ni d'un service
Chroma actif, et ne consomment aucun appel OpenAI payant.

## Décision

- **Pas de nettoyage automatique de la base entre les tests.** Le profil par
  défaut et les faits créés persistent d'une exécution à l'autre — c'est un
  choix volontaire pour rester simple (pas de fixture de transaction/rollback
  à maintenir) sur un projet personnel en développement local. Si le besoin
  de tests parfaitement isolés apparaît (CI partagée, jeux de données de test
  volumineux), on introduira une fixture de rollback par test à ce moment-là.

## Vérification faite dans ce tour

Sans Docker actif dans ce sandbox, la suite a été exécutée une fois avec
PostgreSQL remplacé par SQLite et Redis par `fakeredis` (substitution locale
temporaire, non commitée) : les 9 tests passent. Le comportement contre de
vrais PostgreSQL/Redis (`docker-compose up`) reste à confirmer en local.
