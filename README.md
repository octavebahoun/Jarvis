# Jarvis

Agent IA personnel, construit par phases : un cœur de conversation avec
mémoire et profil (Phase 1), puis un agent capable de raisonner, planifier et
agir via des outils sandboxés (Phase 2). Les phases suivantes (automatisation,
dashboard, voix) sont planifiées mais non commencées.

## Vision

L'objectif n'est pas un chatbot de plus, mais un système qui **connaît son
utilisateur** (profil, mémoire court et long terme, mémoire vectorielle) et
qui peut progressivement **agir pour lui** (recherche web, lecture de
fichiers, exécution de code, navigation web) — toujours avec un plan explicite
et une validation humaine avant toute action sensible.

## Architecture

<svg width="720" height="210" viewBox="0 0 720 210" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Architecture de Jarvis">
  <rect x="8" y="70" width="130" height="64" rx="10" fill="none" stroke="#0891b2" stroke-width="2"/>
  <text x="73" y="97" text-anchor="middle" font-size="13" font-family="Helvetica, Arial, sans-serif" font-weight="600" fill="#0891b2">Frontend</text>
  <text x="73" y="115" text-anchor="middle" font-size="10" font-family="Helvetica, Arial, sans-serif" fill="#64748b">Next.js</text>

  <line x1="138" y1="102" x2="182" y2="102" stroke="#94a3b8" stroke-width="2"/>

  <rect x="182" y="70" width="130" height="64" rx="10" fill="none" stroke="#0891b2" stroke-width="2"/>
  <text x="247" y="97" text-anchor="middle" font-size="13" font-family="Helvetica, Arial, sans-serif" font-weight="600" fill="#0891b2">API</text>
  <text x="247" y="115" text-anchor="middle" font-size="10" font-family="Helvetica, Arial, sans-serif" fill="#64748b">FastAPI</text>

  <line x1="312" y1="102" x2="356" y2="102" stroke="#94a3b8" stroke-width="2"/>

  <rect x="356" y="14" width="150" height="176" rx="10" fill="none" stroke="#7c3aed" stroke-width="2"/>
  <text x="431" y="38" text-anchor="middle" font-size="13" font-family="Helvetica, Arial, sans-serif" font-weight="600" fill="#7c3aed">Agent</text>
  <text x="431" y="64" text-anchor="middle" font-size="10" font-family="Helvetica, Arial, sans-serif" fill="#64748b">Controller</text>
  <text x="431" y="86" text-anchor="middle" font-size="10" font-family="Helvetica, Arial, sans-serif" fill="#64748b">Planner</text>
  <text x="431" y="108" text-anchor="middle" font-size="10" font-family="Helvetica, Arial, sans-serif" fill="#64748b">Reasoning</text>
  <text x="431" y="130" text-anchor="middle" font-size="10" font-family="Helvetica, Arial, sans-serif" fill="#64748b">Executor</text>
  <text x="431" y="152" text-anchor="middle" font-size="10" font-family="Helvetica, Arial, sans-serif" fill="#64748b">Identity</text>

  <line x1="506" y1="55" x2="550" y2="55" stroke="#94a3b8" stroke-width="2"/>
  <line x1="506" y1="150" x2="550" y2="150" stroke="#94a3b8" stroke-width="2"/>

  <rect x="550" y="24" width="162" height="62" rx="10" fill="none" stroke="#059669" stroke-width="2"/>
  <text x="631" y="49" text-anchor="middle" font-size="13" font-family="Helvetica, Arial, sans-serif" font-weight="600" fill="#059669">Memoire</text>
  <text x="631" y="66" text-anchor="middle" font-size="9.5" font-family="Helvetica, Arial, sans-serif" fill="#64748b">Redis / Postgres / Chroma</text>

  <rect x="550" y="118" width="162" height="62" rx="10" fill="none" stroke="#d97706" stroke-width="2"/>
  <text x="631" y="143" text-anchor="middle" font-size="13" font-family="Helvetica, Arial, sans-serif" font-weight="600" fill="#d97706">Tools</text>
  <text x="631" y="160" text-anchor="middle" font-size="9.5" font-family="Helvetica, Arial, sans-serif" fill="#64748b">Sandbox Docker</text>
</svg>

Le détail des couches (Identity Core, mémoire, raisonnement, planificateur,
outils, contrôleur) est dans [`architecture.md`](./architecture.md).

## Stack technique

| Couche | Technologie |
|---|---|
| Frontend | Next.js, React, Tailwind CSS |
| API | FastAPI, Pydantic v2 |
| Agent / raisonnement | LangChain, OpenAI ou OpenRouter (modèles gratuits `:free`) |
| Base relationnelle | PostgreSQL, SQLAlchemy 2.0, Alembic |
| Mémoire court terme | Redis |
| Mémoire vectorielle (RAG) | ChromaDB, embeddings OpenAI ou MiniLM local (gratuit) |
| Tâches asynchrones | Celery + Redis |
| Sandbox d'exécution | Docker (SDK Python) |
| Tests | pytest, Playwright |

Les fournisseurs de LLM et d'embeddings sont interchangeables par variable
d'environnement (`CHAT_PROVIDER`, `EMBEDDING_PROVIDER`) — aucune dépendance
stricte à une API payante pour faire tourner le projet.

## État du projet

<svg width="720" height="150" viewBox="0 0 720 150" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Feuille de route de Jarvis">
  <line x1="90" y1="70" x2="630" y2="70" stroke="#94a3b8" stroke-width="2"/>

  <circle cx="90" cy="70" r="22" fill="#059669" stroke="#059669" stroke-width="2"/>
  <text x="90" y="76" text-anchor="middle" font-size="13" font-family="Helvetica, Arial, sans-serif" font-weight="700" fill="#ffffff">1</text>
  <text x="90" y="24" text-anchor="middle" font-size="12" font-family="Helvetica, Arial, sans-serif" font-weight="600" fill="#059669">Phase 1</text>
  <text x="90" y="40" text-anchor="middle" font-size="10" font-family="Helvetica, Arial, sans-serif" fill="#64748b">Chat, memoire, profil</text>
  <text x="90" y="112" text-anchor="middle" font-size="10" font-family="Helvetica, Arial, sans-serif" fill="#059669">Termine</text>

  <circle cx="270" cy="70" r="22" fill="#059669" stroke="#059669" stroke-width="2"/>
  <text x="270" y="76" text-anchor="middle" font-size="13" font-family="Helvetica, Arial, sans-serif" font-weight="700" fill="#ffffff">2</text>
  <text x="270" y="24" text-anchor="middle" font-size="12" font-family="Helvetica, Arial, sans-serif" font-weight="600" fill="#059669">Phase 2</text>
  <text x="270" y="40" text-anchor="middle" font-size="10" font-family="Helvetica, Arial, sans-serif" fill="#64748b">Agent, outils, plans</text>
  <text x="270" y="112" text-anchor="middle" font-size="10" font-family="Helvetica, Arial, sans-serif" fill="#059669">Termine</text>

  <circle cx="450" cy="70" r="22" fill="none" stroke="#94a3b8" stroke-width="2"/>
  <text x="450" y="76" text-anchor="middle" font-size="13" font-family="Helvetica, Arial, sans-serif" font-weight="700" fill="#94a3b8">3</text>
  <text x="450" y="24" text-anchor="middle" font-size="12" font-family="Helvetica, Arial, sans-serif" font-weight="600" fill="#64748b">Phase 3</text>
  <text x="450" y="40" text-anchor="middle" font-size="10" font-family="Helvetica, Arial, sans-serif" fill="#64748b">Automatisation, dashboard</text>
  <text x="450" y="112" text-anchor="middle" font-size="10" font-family="Helvetica, Arial, sans-serif" fill="#94a3b8">Planifie</text>

  <circle cx="630" cy="70" r="22" fill="none" stroke="#94a3b8" stroke-width="2"/>
  <text x="630" y="76" text-anchor="middle" font-size="13" font-family="Helvetica, Arial, sans-serif" font-weight="700" fill="#94a3b8">4</text>
  <text x="630" y="24" text-anchor="middle" font-size="12" font-family="Helvetica, Arial, sans-serif" font-weight="600" fill="#64748b">Phase 4</text>
  <text x="630" y="40" text-anchor="middle" font-size="10" font-family="Helvetica, Arial, sans-serif" fill="#64748b">Voix, controle OS</text>
  <text x="630" y="112" text-anchor="middle" font-size="10" font-family="Helvetica, Arial, sans-serif" fill="#94a3b8">Planifie</text>
</svg>

**Phase 1 — chat, mémoire, profil.** Chat avec streaming, mémoire court terme
(Redis), long terme (faits en base) et vectorielle (RAG via Chroma), profil
utilisateur, dégradation propre en cas de panne LLM ou mémoire. Journal
détaillé : [`docs/phase1/`](./docs/phase1/).

**Phase 2 — agent, outils, plans.** Le planificateur décide, via le LLM, si
une demande nécessite des outils (recherche web, lecture de fichiers,
exécution de code, navigation web) ou reste une simple conversation. Un plan
proposé doit être **validé explicitement** avant exécution ; chaque outil
sensible tourne dans un container Docker jetable, sans accès réseau sauf
quand strictement nécessaire, avec suppression garantie et timeout strict.
Une synthèse en langage naturel est produite une fois le plan terminé.
Journal détaillé : [`docs/phase2/`](./docs/phase2/).

**Phases 3 et 4 — planifiées.** Automatisation de tâches récurrentes et
dashboard de contrôle (Phase 3), puis interface vocale et contrôle du système
(Phase 4). Non commencées ; voir [`phase3.md`](./phase3.md) et
[`phase4.md`](./phase4.md).

## Démarrage rapide

Prérequis : Docker et Docker Compose.

```bash
git clone <url-du-repo>
cd Jarvis

cp .env.example .env
# renseigner au minimum une clé LLM (OpenAI ou OpenRouter) dans .env

docker compose up -d --build
```

L'API est disponible sur `http://localhost:8080`, le frontend sur
`http://localhost:3000` (une fois démarré via `npm run dev` dans
`frontend/`, ou son propre service si ajouté au compose).

Les migrations de base de données (Alembic) sont appliquées automatiquement
au démarrage des services `backend` et `worker`.

Détails d'installation, de configuration et de tests par composant :
[`backend/README.md`](./backend/README.md) et
[`frontend/README.md`](./frontend/README.md).

## Structure du projet

```
Jarvis/
├── backend/         API FastAPI, agent, mémoire, outils, tâches Celery
├── frontend/         Interface Next.js (chat, profil, mémoire, suivi de plans)
├── docs/
│   ├── phase1/       Journal d'implémentation Phase 1
│   ├── phase2/       Journal d'implémentation Phase 2
│   └── checklist-test-manuel.md
├── sandbox/          Répertoire exposé au tool file_reader
├── docker-compose.yml
├── architecture.md   Détail des couches du système
└── phase1.md … phase4.md   Spécifications de chaque phase
```

## Sécurité et validation humaine

Les outils capables d'avoir un effet réel (exécution de code, navigation web)
sont marqués `requires_validation` : un plan les impliquant reste en attente
tant qu'il n'a pas été approuvé explicitement. Leur exécution a lieu dans un
container Docker isolé et éphémère, avec limites de mémoire/CPU et timeout,
supprimé systématiquement après usage.
