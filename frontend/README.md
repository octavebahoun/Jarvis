# Frontend — Jarvis-like

Frontend du projet **Double Numérique Intelligent** construit avec **Next.js** (App Router).

## Objectif

Fournir l’interface utilisateur pour :

- dialoguer avec l’agent,
- visualiser les réponses et le contexte,
- évoluer vers un dashboard (phases suivantes).

## État actuel (index du projet)

Le frontend est actuellement au stade **template Next.js** :

- page d’accueil par défaut dans `app/page.tsx`,
- layout global et styles de base en place,
- dépendances UI déjà installées dans `package.json` (Framer Motion, Lucide, Three.js),
- structure prête pour accueillir des composants métier.

## Stack frontend

- Next.js 16
- React 19
- TypeScript
- Tailwind CSS v4
- ESLint

## Scripts disponibles

- `npm run dev` : lancement en développement (port 3000)
- `npm run build` : build de production
- `npm run start` : démarrage en mode production
- `npm run lint` : vérification lint

## Lancement rapide

1. Installer les dépendances :
   - `npm install`
2. Démarrer l’application :
   - `npm run dev`
3. Ouvrir :
   - `http://localhost:3000`

## Connexion au backend

Le backend FastAPI est prévu sur le port `8080` (via Docker Compose à la racine).

Recommandation :

- centraliser les appels API dans un module dédié (ex: `lib/api.ts`),
- utiliser des variables d’environnement (`NEXT_PUBLIC_API_URL`) pour l’URL du backend.

## Priorités de développement frontend

1. Remplacer la page template par une interface de chat.
2. Créer les composants principaux (`ChatWindow`, `InputBar`, `MessageItem`).
3. Ajouter un client API typé pour `POST /chat`, `GET/POST /memory`, `GET/PUT /profile`.
4. Gérer les états UX (loading, erreurs, reconnect, historique).
5. Préparer un dashboard progressif pour la phase 3.

## Notes

- Les fichiers [AGENTS.md](AGENTS.md) et [CLAUDE.md](CLAUDE.md) contiennent des consignes de contexte pour assistants/outils.
- Le README racine n’a pas été modifié, conformément à la consigne.
