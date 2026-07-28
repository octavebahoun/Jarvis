# 05 — Interface chat (frontend)

## Ce qui a été construit

- `frontend/lib/api.ts` : client HTTP minimal vers le backend
  (`NEXT_PUBLIC_API_URL`, défaut `http://localhost:8080`) — `sendChatMessage`,
  `getProfile`.
- `frontend/components/ChatWindow.tsx` : affichage de la liste des messages
  (bulles utilisateur/assistant), auto-scroll vers le dernier message.
- `frontend/components/InputBar.tsx` : zone de saisie (textarea + bouton
  Envoyer), soumission avec `Entrée` (`Maj+Entrée` pour une nouvelle ligne).
- `frontend/app/chat/page.tsx` : nouvelle route `/chat`, page client qui gère
  l'état de la conversation, génère un `session_id` (`crypto.randomUUID()`)
  côté client au chargement, et relie `ChatWindow` + `InputBar` à l'API.
- `frontend/app/page.tsx` : ajout d'un bouton "Ouvrir le chat" sur la page
  d'accueil existante, qui pointe vers `/chat`.

## Décisions

- **La page d'accueil existante (`app/page.tsx`) reste la vitrine du projet**,
  telle qu'elle avait déjà été construite (landing page avec vision,
  architecture, roadmap). Le chat devient une route dédiée `/chat` plutôt que
  de remplacer cette page, pour ne pas perdre ce travail existant.
- **`session_id` généré côté client, pas de persistance de session entre
  rechargements de page pour l'instant.** La Phase 1 demande une mémoire
  court terme "session active" — un identifiant de session par onglet suffit ;
  la persistance de session (reprendre une conversation après fermeture du
  navigateur) n'est pas dans le scope explicite de la Phase 1.

## Reste à vérifier

Le serveur de dev Next.js n'a pas pu être lancé/testé dans un navigateur réel
dans ce tour (à faire au prochain lancement local : `npm run dev` puis ouvrir
`/chat`, avec le backend + Docker Compose démarrés).
