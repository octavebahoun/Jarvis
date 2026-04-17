# Architecture — Double Numérique Intelligent

## Stack technique

| Couche           | Technologie             | Rôle                           |
| ---------------- | ----------------------- | ------------------------------ |
| Backend          | Python + FastAPI        | API REST + orchestration agent |
| IA               | LangChain + OpenAI API  | Raisonnement, tools, mémoire   |
| DB relationnelle | PostgreSQL (JSONB)      | Profil utilisateur, historique |
| DB vectorielle   | Chroma                  | Mémoire sémantique (RAG)       |
| Cache            | Redis                   | Sessions, file de tâches       |
| Frontend         | Next.js + Tailwind      | Interface chat + dashboard     |
| Infra            | Docker + Docker Compose | Déploiement unifié             |

---

## Structure de fichiers

```
jarvis/
│
├── backend/
│   ├── main.py                  # Entrée FastAPI
│   ├── config.py                # Variables d'env, settings globaux
│   │
│   ├── api/
│   │   ├── routes/
│   │   │   ├── chat.py          # POST /chat → déclenche l'agent
│   │   │   ├── memory.py        # GET/POST /memory → lecture/écriture mémoire
│   │   │   └── profile.py       # GET/PUT /profile → Identity Core
│   │   └── deps.py              # Dépendances FastAPI (auth, DB session)
│   │
│   ├── agent/
│   │   ├── controller.py        # 🧠 Cerveau : reçoit requête → orchestre tout
│   │   ├── reasoning.py         # Analyse la requête, construit le prompt enrichi
│   │   ├── planner.py           # Décompose un objectif en étapes
│   │   └── executor.py          # Exécute le plan via tools
│   │
│   ├── memory/
│   │   ├── short_term.py        # Historique de conversation (Redis ou in-memory)
│   │   ├── long_term.py         # Faits persistants (PostgreSQL)
│   │   └── vector_store.py      # Embeddings + recherche sémantique (Chroma)
│   │
│   ├── identity/
│   │   └── profile.py           # Chargement / mise à jour du profil utilisateur
│   │
│   ├── tools/
│   │   ├── file_reader.py       # Lire des fichiers locaux
│   │   ├── code_executor.py     # Exécuter du code Python en sandbox
│   │   └── web_search.py        # Recherche web via API
│   │
│   ├── learning/
│   │   └── feedback_loop.py     # Analyse interactions → met à jour mémoire long terme
│   │
│   └── db/
│       ├── models.py            # Modèles SQLAlchemy (User, Memory, Conversation)
│       └── session.py           # Connexion PostgreSQL
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx             # Interface chat principale
│   │   └── dashboard/
│   │       └── page.tsx         # Dashboard (Phase 3+)
│   ├── components/
│   │   ├── ChatWindow.tsx       # Affichage des messages
│   │   ├── InputBar.tsx         # Champ de saisie
│   │   └── MemoryPanel.tsx      # Visualisation mémoire (optionnel MVP)
│   └── lib/
│       └── api.ts               # Appels vers le backend FastAPI
│
├── docker-compose.yml           # Backend + DB + Redis + Chroma
├── .env                         # Clés API, config DB
└── README.md
```

---

## Flux d'une requête

```
Utilisateur (chat)
    ↓
POST /chat  (FastAPI)
    ↓
controller.py
    ├── Charge profil (identity/profile.py)
    ├── Récupère contexte court terme (memory/short_term.py)
    ├── Recherche sémantique (memory/vector_store.py)
    ↓
reasoning.py  → construit le prompt enrichi
    ↓
LangChain Agent (OpenAI)
    ├── Si tâche simple → réponse directe
    └── Si tâche complexe → planner.py → executor.py → tools/
    ↓
Réponse retournée + sauvegardée en mémoire
```

## Décisions d'architecture clés

**Pourquoi FastAPI et pas Express ?**
L'écosystème IA Python (LangChain, Chroma, OpenAI SDK) est plus mature. FastAPI offre des performances async comparables à Node.

**Pourquoi Chroma et pas FAISS ?**
Chroma est une base vectorielle avec persistance native et API REST intégrée, ce qui simplifie le déploiement Docker. FAISS reste plus performant à grande échelle.

**Pourquoi séparer short_term / long_term / vector_store ?**
Trois natures de mémoire différentes : temporalité (session vs permanent), structure (texte vs vecteur), et accès (séquentiel vs sémantique). Les mélanger crée une dette technique dès le MVP.

**Pourquoi un `controller.py` central ?**
L'agent a besoin d'un point d'entrée unique qui décide quoi appeler et dans quel ordre. Cela évite que chaque route API réimplémente la logique d'orchestration.
