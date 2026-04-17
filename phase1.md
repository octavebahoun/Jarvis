# 🧠 Double Numérique Intelligent — Phase 1 MVP (Version Finalisée)

> Agent IA personnel agentique — version augmentée de l’utilisateur.

---

# 🎯 Objectif de la Phase 1

Construire un **chat intelligent avec mémoire avancée et personnalisation utilisateur**.

## ✅ Capacités finales de la Phase 1

Le système peut :

* 💬 Répondre comme un assistant IA classique
* 🧠 Maintenir le contexte court terme (session active)
* 📚 Stocker des informations durables sur l’utilisateur
* 🔎 Effectuer une recherche sémantique (mémoire vectorielle)
* 🎯 Adapter ses réponses au profil utilisateur

## ❌ Hors scope Phase 1

* Agents autonomes
* Planification de tâches
* Exécution d’actions système
* Voice / audio
* Automatisation externe

---

# ⚙️ Stack technique

| Couche           | Technologie        | Version |
| ---------------- | ------------------ | ------- |
| Backend          | Python + FastAPI   | 3.11+   |
| IA / Agent       | LangChain          | 0.2+    |
| LLM              | OpenAI GPT-4o      | API     |
| DB relationnelle | PostgreSQL         | 15+     |
| DB vectorielle   | ChromaDB           | 0.5+    |
| Cache            | Redis              | 7+      |
| Frontend         | Next.js + Tailwind | 14+     |
| Infra            | Docker + Compose   | —       |

---

# 🗂️ Architecture du projet

```
jarvis/
│
├── backend/
│   ├── main.py
│   ├── config.py
│   │
│   ├── api/
│   │   ├── routes/
│   │   │   ├── chat.py
│   │   │   ├── memory.py
│   │   │   └── profile.py
│   │   └── deps.py
│   │
│   ├── agent/
│   │   ├── controller.py   # Orchestrateur central
│   │   └── reasoning.py    # Prompt + enrichissement contexte
│   │
│   ├── memory/
│   │   ├── short_term.py   # Redis / session active
│   │   ├── long_term.py    # PostgreSQL (faits utilisateur)
│   │   └── vector_store.py # ChromaDB (RAG)
│   │
│   ├── identity/
│   │   └── profile.py      # Profil utilisateur
│   │
│   └── db/
│       ├── models.py
│       └── session.py
│
├── frontend/
│   ├── app/
│   │   └── page.tsx
│   ├── components/
│   │   ├── ChatWindow.tsx
│   │   └── InputBar.tsx
│   └── lib/
│       └── api.ts
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

# 🔄 Flux d’une requête

```
Utilisateur
   ↓
POST /chat (FastAPI)
   ↓
controller.py
   ├── Chargement profil utilisateur
   ├── Récupération mémoire court terme (Redis)
   ├── Recherche mémoire vectorielle (Chroma)
   ↓
reasoning.py
   └── Construction du prompt enrichi
   ↓
LLM (GPT-4o via LangChain)
   ↓
Réponse utilisateur
   ↓
Sauvegarde mémoire (PostgreSQL + Chroma)
```

---

# 🚀 Installation

## Prérequis

* Docker + Docker Compose
* Node.js 20+
* Clé API OpenAI

---

## Lancement

```bash
# Cloner le projet
git clone https://github.com/ton-user/jarvis.git
cd jarvis

# Variables d'environnement
cp .env.example .env

# Lancer backend + DB + cache
docker-compose up -d

# Frontend
cd frontend
npm install
npm run dev
```

---

## ⚙️ Variables d’environnement

```env
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://user:password@localhost:5432/jarvis
REDIS_URL=redis://localhost:6379
CHROMA_HOST=localhost
CHROMA_PORT=8000
SECRET_KEY=your-secret
```

---

# 📡 API — Phase 1

## POST /chat

```json
{
  "message": "Explique les hooks React",
  "session_id": "abc123"
}
```

## Response

```json
{
  "reply": "...",
  "session_id": "abc123"
}
```

---

## GET /profile

```json
{
  "username": "octave",
  "tech_stack": ["React", "Node.js", "Python"],
  "preferences": {}
}
```

---

## GET /memory?type=long_term

Retourne les souvenirs utilisateur persistants.

---

# 🧠 Système de mémoire

## 🔹 Short-term (Redis)

* Session active
* Historique conversation
* TTL court (ex: 2h)

## 🔹 Long-term (PostgreSQL)

* Profil utilisateur
* Faits importants
* Préférences

## 🔹 Vectoriel (ChromaDB)

* Embeddings
* Recherche sémantique
* RAG contextuel

---

# 🔐 Sécurité

* JWT authentication
* Isolation des utilisateurs
* Secrets via .env uniquement
* Aucun accès direct frontend → DB

---

# 📐 Règles d’architecture

* Logique métier uniquement dans `controller.py`
* Aucune logique IA dans les routes
* Memory / identity / agent totalement découplés
* Appels OpenAI uniquement dans `reasoning.py`

---

# 🗺️ Roadmap

| Phase   | Objectif                |
| ------- | ----------------------- |
| Phase 1 | Chat + mémoire + profil |
| Phase 2 | Tools + agentic actions |
| Phase 3 | Automation + dashboard  |
| Phase 4 | Voice + système Jarvis  |

---

# 👤 Vision

Un système capable de :

> Comprendre l’utilisateur, mémoriser son contexte et adapter ses réponses de manière personnalisée.

---

# 🔥 Résultat attendu Phase 1

Un **chat IA intelligent avec mémoire persistante et comportement personnalisé**, base solide du futur agent autonome.
