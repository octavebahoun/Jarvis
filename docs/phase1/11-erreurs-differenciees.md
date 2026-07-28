# 11 — Erreurs différenciées côté frontend

## Ce qui a été construit

- `lib/api.ts` : nouvelle classe `ApiError` (porte le `status` HTTP), levée
  par `request()` et `streamChatMessage()` au lieu d'une `Error` générique.
  Une erreur réseau (backend injoignable) reste une `TypeError` native de
  `fetch`, donc **pas** une `ApiError` — c'est ce qui permet de distinguer les
  deux cas côté appelant.
- `app/chat/page.tsx` : `describeSendError(err)` choisit le message affiché
  selon le type d'échec :
  - pas une `ApiError` (réseau) → "Impossible de joindre Jarvis. Vérifie que
    le backend tourne (docker-compose up)."
  - `ApiError` avec `status === 422` → "Message invalide."
  - autre `ApiError` → "Erreur serveur inattendue (code X)."
  - le marqueur de panne LLM en cours de flux (`failed`, voir doc 10) garde
    son propre message : "Le LLM a rencontré une erreur pendant la génération
    de la réponse."

## Pourquoi pas de cas 502 explicite sur `/chat/stream`

`/chat/stream` renvoie toujours un `200` dès le premier octet (StreamingResponse) :
une panne LLM ne peut plus se traduire par un vrai code d'erreur HTTP une fois
le flux démarré (voir doc 10, `STREAM_ERROR_MARKER`). Le seul `ApiError` que
`streamChatMessage` peut réellement lever aujourd'hui, c'est un `422` (message
vide, rejeté avant même que le flux ne démarre) ou un statut inattendu (proxy,
mauvaise config réseau...).

## Vérifié

- `tsc --noEmit` propre.
- Test réel en navigateur, backend éteint : le message "Impossible de joindre
  Jarvis..." s'affiche bien (capture d'écran), différent du message
  générique précédent.
