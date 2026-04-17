# ⚡ Double Numérique Intelligent — Phase 3 : Assistant Avancé

> L'agent automatise des workflows récurrents et expose un dashboard de contrôle complet.

---

## 📌 Objectif Phase 3

Passer d'un agent réactif (Phase 2) à un **assistant proactif** capable de :
- Exécuter des tâches planifiées sans déclenchement manuel
- Connecter des services externes (GitHub, Notion, calendrier...)
- Exposer un dashboard de contrôle, mémoire et historique

**Prérequis :** Phase 2 stable — Tool System + Planner opérationnels.

---

## ⚙️ Stack — Ajouts Phase 3

| Couche | Technologie | Rôle |
|--------|-------------|------|
| Scheduler | APScheduler / Celery Beat | Tâches automatiques planifiées |
| Intégrations | GitHub API, Notion API, Google Calendar | Actions sur services externes |
| Monitoring | Prometheus + Grafana (optionnel) | Observabilité système |
| Dashboard | Next.js + Recharts / Tremor | Visualisation mémoire + historique |
| Auth OAuth | NextAuth.js | Connexion services tiers |

> Tout le reste est hérité des Phases 1 et 2.

---

## 🗂️ Nouveaux fichiers

```
jarvis/
│
├── backend/
│   ├── agent/
│   │   └── proactive.py         # 🆕 Déclenchement automatique de tâches
│   │
│   ├── tools/
│   │   ├── github.py            # 🆕 Lire/créer issues, PRs, repos
│   │   ├── notion.py            # 🆕 Lire/écrire pages Notion
│   │   └── calendar.py          # 🆕 Lire/créer événements Google Calendar
│   │
│   ├── scheduler/
│   │   ├── jobs.py              # 🆕 Définition des tâches planifiées
│   │   └── registry.py          # 🆕 Registre des automatisations actives
│   │
│   ├── learning/
│   │   └── feedback_loop.py     # ← Étendu : analyse les patterns d'usage
│   │
│   └── api/
│       └── routes/
│           ├── automations.py   # 🆕 CRUD automatisations
│           └── dashboard.py     # 🆕 Données agrégées pour le dashboard
│
└── frontend/
    ├── app/
    │   ├── page.tsx             # ← Chat (inchangé)
    │   └── dashboard/
    │       ├── page.tsx         # 🆕 Dashboard principal
    │       ├── memory/
    │       │   └── page.tsx     # 🆕 Visualisation mémoire long terme
    │       ├── automations/
    │       │   └── page.tsx     # 🆕 Gestion des automatisations
    │       └── history/
    │           └── page.tsx     # 🆕 Historique des actions exécutées
    └── components/
        ├── MemoryGraph.tsx      # 🆕 Graphe des souvenirs
        ├── AutomationCard.tsx   # 🆕 Carte d'une automatisation
        └── ActivityFeed.tsx     # 🆕 Flux d'activité temps réel
```

---

## 🔄 Deux modes de déclenchement

### Mode réactif (hérité Phase 2)
```
Utilisateur → message → agent → action
```

### Mode proactif (nouveau Phase 3)
```
Scheduler (cron / événement)
    ↓
proactive.py
    ├── Récupère les automatisations actives (registry.py)
    ├── Vérifie les conditions de déclenchement
    └── Lance executor.py → tools → résultat
    ↓
Notification push → frontend (WebSocket)
```

---

## 🤖 Système d'automatisation

Une automatisation = un déclencheur + une action + des conditions.

```json
{
  "id": "auto_001",
  "name": "Résumé GitHub quotidien",
  "trigger": {
    "type": "cron",
    "schedule": "0 9 * * 1-5"
  },
  "condition": "repos avec activité depuis hier",
  "action": {
    "tool": "github",
    "task": "résumer les PRs et issues ouvertes"
  },
  "output": "notification + sauvegarde mémoire",
  "active": true
}
```

### Automatisations prévues Phase 3

| Nom | Déclencheur | Action |
|-----|-------------|--------|
| Résumé GitHub | Chaque matin | Résume PRs + issues actives |
| Rappel projets | Chaque lundi | Liste tâches en attente |
| Veille tech | Hebdomadaire | Recherche web → résumé personnalisé |
| Sync Notion | Sur demande | Met à jour les notes de projet |

---

## 📡 Nouveaux endpoints API

### `GET /dashboard/summary`

```json
{
  "memory": {
    "long_term_entries": 42,
    "vector_chunks": 310
  },
  "activity": {
    "tasks_this_week": 17,
    "tools_used": { "file_reader": 8, "github": 6, "web_search": 3 }
  },
  "automations": {
    "active": 3,
    "last_run": "2025-04-17T09:00:00Z"
  }
}
```

### `GET /automations`

Liste toutes les automatisations de l'utilisateur.

### `POST /automations`

Crée une nouvelle automatisation.

### `PUT /automations/:id/toggle`

Active ou désactive une automatisation.

### `GET /history`

```json
[
  {
    "id": "task_xyz",
    "type": "automation",
    "name": "Résumé GitHub quotidien",
    "executed_at": "2025-04-17T09:00:12Z",
    "status": "success",
    "summary": "3 PRs analysées, 1 issue critique détectée"
  }
]
```

---

## 🖥️ Dashboard — Pages

### `/dashboard`
Vue globale : mémoire utilisée, activité récente, automatisations actives, dernières actions.

### `/dashboard/memory`
Exploration de la mémoire long terme et vectorielle — recherche, suppression, édition manuelle.

### `/dashboard/automations`
CRUD complet des automatisations — créer, activer/désactiver, voir les logs d'exécution.

### `/dashboard/history`
Historique complet des actions exécutées par l'agent avec filtres (date, type, outil, statut).

---

## 🔐 Sécurité — Règles Phase 3

- Les tokens OAuth (GitHub, Notion, Google) sont chiffrés en base (AES-256) — jamais en clair
- Chaque automatisation est scopée à l'utilisateur — pas d'accès croisé
- Les automatisations proactives **ne peuvent pas** exécuter `code_executor` sans session active de l'utilisateur
- Limite : max 10 automatisations actives simultanées par utilisateur (MVP)

---

## 📐 Règles de développement — Phase 3

### Architecture

- `proactive.py` utilise les mêmes tools que `executor.py` — pas de duplication
- Le scheduler ne contient aucune logique métier — il appelle uniquement `proactive.py`
- Les intégrations externes (GitHub, Notion...) sont des tools standard enregistrés dans `tools/__init__.py`

### Dashboard

- Le dashboard est **read-only** sur la mémoire vectorielle — pas d'écriture directe via UI
- Toute modification de mémoire passe par l'API, jamais par accès direct à Chroma depuis le frontend

### Git

- Branche dédiée : `feat/phase3-dashboard`
- Les intégrations externes sont développées sur des branches séparées : `feat/tool-github`, `feat/tool-notion`
- Merge sur `main` uniquement après test end-to-end d'une automatisation complète (trigger → exécution → log)

---

## 🗺️ Roadmap globale

| Phase | Durée | Objectif | Statut |
|-------|-------|----------|--------|
| Phase 1 | 1 mois | Chat + mémoire + profil | ✅ |
| Phase 2 | 2–3 mois | Tools + planification + actions | ✅ |
| **Phase 3** | **4–6 mois** | **Automatisation + dashboard** | 🔵 En cours |
| Phase 4 | 6–12 mois | Voix + contrôle système + anticipation | 🔲 |

---

## 👤 Auteur

**Oktav** — Fullstack JS × IA  
Co-fondateur @ Excellence Team  
[LinkedIn](https://linkedin.com) · [GitHub](https://github.com)
