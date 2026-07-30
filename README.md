<div align="center">

# Jarvis

**Agent IA personnel, construit par phases.**

Un cœur de conversation avec mémoire et profil, puis un agent capable de
raisonner, planifier et agir via des outils sandboxés.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-Frontend-000000?logo=nextdotjs&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Base%20de%20donn%C3%A9es-4169E1?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-Cache-DC382D?logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)

![Phase 1](https://img.shields.io/badge/Phase%201-Termin%C3%A9-059669)
![Phase 2](https://img.shields.io/badge/Phase%202-Termin%C3%A9-059669)
![Phase 3](https://img.shields.io/badge/Phase%203-Planifi%C3%A9-94a3b8)
![Phase 4](https://img.shields.io/badge/Phase%204-Planifi%C3%A9-94a3b8)

</div>

## Sommaire

- [Vision](#vision)
- [Architecture](#architecture)
- [Stack technique](#stack-technique)
- [État du projet](#état-du-projet)
- [Démarrage rapide](#démarrage-rapide)
- [Structure du projet](#structure-du-projet)
- [Sécurité et validation humaine](#sécurité-et-validation-humaine)

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

<table>
<thead>
<tr><th>Couche</th><th>Technologie</th><th>Rôle</th></tr>
</thead>
<tbody>
<tr>
<td>Frontend</td>
<td><img src="https://img.shields.io/badge/Next.js-000000?logo=nextdotjs&logoColor=white" alt="Next.js"/> <img src="https://img.shields.io/badge/Tailwind_CSS-06B6D4?logo=tailwindcss&logoColor=white" alt="Tailwind CSS"/></td>
<td>Interface chat, profil, mémoire, suivi de plans</td>
</tr>
<tr>
<td>API</td>
<td><img src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white" alt="FastAPI"/> <img src="https://img.shields.io/badge/Pydantic_v2-E92063?logo=pydantic&logoColor=white" alt="Pydantic"/></td>
<td>Routes REST, streaming, validation des schémas</td>
</tr>
<tr>
<td>Agent / raisonnement</td>
<td><img src="https://img.shields.io/badge/LangChain-1C3C3C" alt="LangChain"/> <img src="https://img.shields.io/badge/OpenAI_%2F_OpenRouter-412991?logo=openai&logoColor=white" alt="OpenAI / OpenRouter"/></td>
<td>Prompting, planification, modèles gratuits <code>:free</code> possibles</td>
</tr>
<tr>
<td>Base relationnelle</td>
<td><img src="https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL"/> <img src="https://img.shields.io/badge/SQLAlchemy_2.0-D71F00" alt="SQLAlchemy"/> <img src="https://img.shields.io/badge/Alembic-6BA81E" alt="Alembic"/></td>
<td>Utilisateurs, faits, messages, plans — migrations versionnées</td>
</tr>
<tr>
<td>Mémoire court terme</td>
<td><img src="https://img.shields.io/badge/Redis-DC382D?logo=redis&logoColor=white" alt="Redis"/></td>
<td>Historique de conversation (TTL)</td>
</tr>
<tr>
<td>Mémoire vectorielle</td>
<td><img src="https://img.shields.io/badge/ChromaDB-FF6F00" alt="ChromaDB"/></td>
<td>RAG — embeddings OpenAI ou MiniLM local (gratuit)</td>
</tr>
<tr>
<td>Tâches asynchrones</td>
<td><img src="https://img.shields.io/badge/Celery-37814A?logo=celery&logoColor=white" alt="Celery"/></td>
<td>Exécution des plans approuvés, hors requête HTTP</td>
</tr>
<tr>
<td>Sandbox d'exécution</td>
<td><img src="https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white" alt="Docker"/></td>
<td>Containers jetables pour les outils sensibles</td>
</tr>
<tr>
<td>Tests</td>
<td><img src="https://img.shields.io/badge/pytest-0A9EDC?logo=pytest&logoColor=white" alt="pytest"/> <img src="https://img.shields.io/badge/Playwright-2EAD33?logo=playwright&logoColor=white" alt="Playwright"/></td>
<td>Suite backend + vérification fonctionnelle navigateur</td>
</tr>
</tbody>
</table>

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

<table>
<tr>
<td valign="top" width="50%">

**Phase 1 — chat, mémoire, profil** ![Termine](https://img.shields.io/badge/-Termin%C3%A9-059669)

Chat avec streaming, mémoire court terme (Redis), long terme (faits en base)
et vectorielle (RAG via Chroma), profil utilisateur, dégradation propre en
cas de panne LLM ou mémoire.

Journal détaillé : [`docs/phase1/`](./docs/phase1/)

</td>
<td valign="top" width="50%">

**Phase 2 — agent, outils, plans** ![Termine](https://img.shields.io/badge/-Termin%C3%A9-059669)

Le planificateur décide, via le LLM, si une demande nécessite des outils
(recherche web, lecture de fichiers, exécution de code, navigation web) ou
reste une simple conversation. Un plan proposé doit être **validé
explicitement** avant exécution ; chaque outil sensible tourne dans un
container Docker jetable. Une synthèse en langage naturel est produite une
fois le plan terminé.

Journal détaillé : [`docs/phase2/`](./docs/phase2/)

</td>
</tr>
<tr>
<td valign="top" width="50%">

**Phase 3 — automatisation, dashboard** ![Planifie](https://img.shields.io/badge/-Planifi%C3%A9-94a3b8)

Déclenchement automatique de tâches planifiées, intégrations externes
(GitHub, Notion, calendrier), dashboard de suivi. Non commencée — voir
[`phase3.md`](./phase3.md).

</td>
<td valign="top" width="50%">

**Phase 4 — voix, contrôle OS** ![Planifie](https://img.shields.io/badge/-Planifi%C3%A9-94a3b8)

Interface vocale (entrée/sortie), contrôle du système d'exploitation,
coordination multi-agents. Non commencée — voir [`phase4.md`](./phase4.md).

</td>
</tr>
</table>

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

<details>
<summary>Voir l'arborescence</summary>

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

</details>

## Sécurité et validation humaine

Les outils capables d'avoir un effet réel (exécution de code, navigation web)
sont marqués `requires_validation` : un plan les impliquant reste en attente
tant qu'il n'a pas été approuvé explicitement. Leur exécution a lieu dans un
container Docker isolé et éphémère, avec limites de mémoire/CPU et timeout,
supprimé systématiquement après usage.
