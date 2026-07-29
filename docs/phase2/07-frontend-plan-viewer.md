# 07 — Frontend : PlanViewer, ToolCallCard, TaskStatus

## Ce qui a été construit

- `lib/api.ts` : `ChatMessage` devient une union (`user`/`assistant` texte ou
  `plan` avec un `planId`). `streamChatMessage` détecte le `PLAN_MARKER`
  (doit rester identique à `agent.controller.PLAN_MARKER`) dans le flux et
  renvoie `{ type: "plan", planId }` au lieu de `{ type: "reply", ... }` —
  sans jamais afficher le marqueur brut pendant le streaming (vérifié avant
  d'appeler `onChunk`). Nouvelles fonctions `getTask`, `approveTask`,
  `getTaskWebSocketUrl`.
- `components/TaskStatus.tsx` : badge coloré par statut (pending/approved/
  running/done/failed).
- `components/ToolCallCard.tsx` : une étape du plan — tool, description,
  statut, résultat ou erreur.
- `components/PlanViewer.tsx` : charge le plan (`GET /tasks/:id`), affiche le
  bouton "Approuver l'exécution" tant que `status === "pending"`, puis ouvre
  un WebSocket (`/ws/tasks/:id`) pour suivre l'exécution en temps réel jusqu'à
  un statut terminal.
- `ChatWindow.tsx` : un message de rôle `"plan"` rend `<PlanViewer>` au lieu
  d'une bulle de texte, directement dans le fil de conversation.

## Décision : le WebSocket ne s'ouvre qu'une fois, pas à chaque changement de statut

`PlanViewer` garde un état `hasStarted` (stable une fois passé à `true`)
plutôt que de dépendre directement de `plan.status` pour décider d'ouvrir le
WebSocket : sinon, chaque message reçu du WebSocket (qui change `plan.status`)
aurait redéclenché l'effet, fermant et rouvrant une connexion à chaque
transition (`approved` → `running` → `done`).

## Vérifié

`tsc --noEmit` et `npm run lint` propres, build de production OK. **Test réel
en navigateur** contre un backend simulé (planner forcé à proposer un plan,
`file_reader` avec un délai artificiel de 2,5s pour observer l'état "en
cours", exécution Celery simulée par un thread local — pas de vrai
broker/worker) : trois captures d'écran confirment le flux complet —
proposition du plan (pending) → clic "Approuver" → statut "En cours..." en
temps réel (plan et étape) → statut "Terminé" avec le résultat affiché
(contenu du fichier lu).

## Reste à vérifier

Un vrai worker Celery + Redis + Docker (code_executor / browser_automation
réellement sandboxés) — nécessite l'environnement complet sur ta machine,
pas reproductible dans ce sandbox.
