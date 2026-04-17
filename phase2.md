# 🤖 Double Numérique Intelligent — Phase 2 : Agent

> L'agent peut maintenant planifier, utiliser des outils et exécuter des actions — avec validation humaine.

---

## 📌 Objectif Phase 2

Transformer le chat intelligent (Phase 1) en **agent semi-autonome contrôlé**.

**Ce qui s'ajoute :**
- Décomposition d'un objectif en étapes (Planner)
- Exécution d'actions via des outils (Tool System)
- Validation humaine avant chaque action sensible
- Suivi de l'avancement des tâches

**Prérequis :** Phase 1 stable et déployée.

---

## ⚙️ Stack — Ajouts Phase 2

| Couche | Technologie | Rôle |
|--------|-------------|------|
| Agent framework | LangChain Agents | Orchestration tools + ReAct |
| Sandbox Python | subprocess / Docker exec | Exécution sécurisée de code |
| File system | pathlib + watchdog | Lecture/écriture fichiers |
| Web search | Serper API / Tavily | Recherche web |
| Queue de tâches | Redis + Celery | Exécution async des plans |
| Websocket | FastAPI WebSocket | Feedback temps réel à l'UI |

> Tout le reste (PostgreSQL, Chroma, Redis, Next.js) est hérité de la Phase 1.

---

## 🗂️ Nouveaux fichiers

```
jarvis/
│
├── backend/
│   ├── agent/
│   │   ├── controller.py        # ← Mis à jour : gère maintenant les plans
│   │   ├── reasoning.py         # ← Inchangé
│   │   ├── planner.py           # 🆕 Décompose un objectif en étapes
│   │   └── executor.py          # 🆕 Exécute les étapes via tools
│   │
│   ├── tools/
│   │   ├── __init__.py          # 🆕 Registre des tools disponibles
│   │   ├── file_reader.py       # 🆕 Lire des fichiers locaux
│   │   ├── code_executor.py     # 🆕 Exécuter du code Python en sandbox
│   │   └── web_search.py        # 🆕 Recherche web via API
│   │
│   ├── tasks/
│   │   ├── worker.py            # 🆕 Worker Celery
│   │   └── task_store.py        # 🆕 Suivi état des tâches (PostgreSQL)
│   │
│   └── api/
│       └── routes/
│           ├── chat.py          # ← Mis à jour : peut retourner un plan
│           └── tasks.py         # 🆕 GET /tasks/:id → état d'une tâche
│
└── frontend/
    └── components/
        ├── PlanViewer.tsx        # 🆕 Affiche le plan étape par étape
        ├── ToolCallCard.tsx      # 🆕 Affiche l'action en attente de validation
        └── TaskStatus.tsx        # 🆕 Suivi temps réel via WebSocket
```

---

## 🔄 Flux d'une requête agentique

```
[Utilisateur] → "Analyse mon fichier main.py et propose des améliorations"
                    ↓
            controller.py
            ├── Détecte : tâche complexe → mode agent
            ├── Charge profil + mémoire (Phase 1)
            └── Lance planner.py
                    ↓
            planner.py → génère plan structuré :
            {
              "steps": [
                { "tool": "file_reader", "args": { "path": "main.py" } },
                { "tool": "reasoning",   "args": { "task": "analyser le code" } }
              ]
            }
                    ↓
            → Envoyé au frontend (PlanViewer)
            → Utilisateur valide ou modifie
                    ↓
            executor.py → exécute étape par étape
            ├── Appelle file_reader.py → lit le fichier
            ├── Appelle reasoning.py → analyse le contenu
            └── Retourne résultat + sauvegarde en mémoire
```

---

## 🛠️ Tool System

Chaque tool est une classe Python standardisée :

```python
class BaseTool:
    name: str
    description: str          # Lu par le LLM pour choisir le bon tool
    requires_validation: bool # Si True → demande confirmation avant exécution

    def run(self, **kwargs) -> str:
        raise NotImplementedError
```

### Tools Phase 2

| Tool | Fichier | Validation requise |
|------|---------|-------------------|
| Lecture fichier | `file_reader.py` | Non |
| Exécution code | `code_executor.py` | **Oui** |
| Recherche web | `web_search.py` | Non |

### Ajouter un tool

1. Créer `tools/mon_tool.py` héritant de `BaseTool`
2. L'enregistrer dans `tools/__init__.py`
3. Le décrire clairement — le LLM s'en sert pour décider quand l'utiliser

---

## 📡 Nouveaux endpoints API

### `POST /chat` — Réponse étendue

```json
// Response (mode agent)
{
  "type": "plan",
  "plan": {
    "id": "plan_abc123",
    "steps": [
      { "id": 1, "tool": "file_reader", "description": "Lire main.py", "status": "pending" },
      { "id": 2, "tool": "reasoning",   "description": "Analyser le code", "status": "pending" }
    ]
  }
}
```

### `POST /tasks/:plan_id/approve`

Valide et lance l'exécution du plan.

### `GET /tasks/:plan_id`

```json
{
  "id": "plan_abc123",
  "status": "running",
  "steps": [
    { "id": 1, "status": "done",    "result": "Fichier lu : 120 lignes" },
    { "id": 2, "status": "running", "result": null }
  ]
}
```

### `WebSocket /ws/tasks/:plan_id`

Stream temps réel de l'avancement du plan vers le frontend.

---

## 🔐 Sécurité — Règles Phase 2

- **Tout code exécuté tourne dans un container Docker isolé** — jamais sur le host directement
- L'accès fichiers est limité à un répertoire sandbox défini dans `.env` (`SANDBOX_PATH`)
- Chaque tool marqué `requires_validation: True` **ne s'exécute pas** sans confirmation explicite de l'utilisateur
- Les résultats d'exécution de code sont tronqués à 10 000 caractères avant d'être envoyés au LLM

---

## 📐 Règles de développement — Phase 2

### Architecture

- `executor.py` appelle les tools — `controller.py` ne les appelle **jamais** directement
- Un tool ne doit jamais appeler un autre tool — c'est le rôle de `executor.py`
- Tout plan généré est persisté en base avant exécution (traçabilité)

### Sécurité code

- Jamais d'exécution de code hors sandbox Docker
- La liste des tools disponibles est définie statiquement dans `tools/__init__.py` — pas de chargement dynamique

### Git

- Branche dédiée : `feat/phase2-agent`
- Merge sur `dev` uniquement après test des 3 tools de base
- Pas de merge sur `main` sans test end-to-end du flux plan → validation → exécution

---

## 🗺️ Roadmap globale

| Phase | Durée | Objectif | Statut |
|-------|-------|----------|--------|
| Phase 1 | 1 mois | Chat + mémoire + profil | ✅ |
| **Phase 2** | **2–3 mois** | **Tools + planification + actions** | 🔵 En cours |
| Phase 3 | 4–6 mois | Automatisation + dashboard | 🔲 |
| Phase 4 | 6–12 mois | Voix + contrôle système + anticipation | 🔲 |

---

## 👤 Auteur

**Oktav** — Fullstack JS × IA  
Co-fondateur @ Excellence Team  
[LinkedIn](https://linkedin.com) · [GitHub](https://github.com)
