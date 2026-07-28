# 04 — API FastAPI

## Ce qui a été construit

- `backend/api/routes/chat.py` : `POST /chat` — reçoit `{message, session_id}`,
  délègue à `agent.controller.handle_chat`, renvoie `{reply, session_id}`
  (format conforme à `phase1.md`).
- `backend/api/routes/profile.py` : `GET /profile` et `PUT /profile` (lecture et
  mise à jour de la stack technique / des préférences).
- `backend/api/routes/memory.py` : `GET /memory?type=short_term|long_term`
  (avec `session_id` requis pour le court terme).
- `backend/main.py` : point d'entrée FastAPI. Utilise un `lifespan` (plutôt que
  l'ancien `@app.on_event("startup")`, déprécié) pour appeler `init_db()` au
  démarrage. CORS ouvert vers `http://localhost:3000` (le frontend Next.js en
  dev). Route `GET /health` pour un check simple.

## Comment ça a été vérifié

Sans Docker disponible dans ce sandbox, la validation s'est faite en deux
temps :

1. **Compilation + import** : tous les modules compilent (`py_compile`) et
   s'importent sans erreur dans un environnement virtuel avec les vraies
   dépendances (FastAPI, SQLAlchemy, Chroma, LangChain...).
2. **Test bout-en-bout avec `TestClient`** : `/health`, `GET/PUT /profile`,
   `POST /chat`, `GET /memory` (court et long terme) ont été appelés sur une
   vraie instance de l'app FastAPI, avec PostgreSQL remplacé par SQLite, Redis
   par `fakeredis`, et l'appel OpenAI par une réponse simulée (aucune clé API ni
   service Docker disponible ici). Résultat : les 6 appels passent, le profil se
   met à jour, l'historique court terme contient bien les 2 messages échangés.

Ce test de fumée n'a pas été commité (il dépend de bibliothèques de test qui ne
sont pas dans `requirements.txt`) : c'est une vérification locale, pas un test
du dépôt. Écrire de vrais tests (pytest + fixtures Docker) est une suite
logique naturelle, mais qui n'était pas demandée pour ce tour ; à faire quand
tu voudras une CI.

## Reste à vérifier

- Comportement réel face à un vrai PostgreSQL/Redis/Chroma (via
  `docker-compose up`) et un vrai appel OpenAI — non testable dans ce sandbox
  (pas de daemon Docker actif, pas de clé API).
