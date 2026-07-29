# 10 — Streaming de la réponse (/chat/stream)

## Ce qui a été construit

- `agent/reasoning.py` : `stream_reply(messages)` — utilise `ChatOpenAI.stream()`
  (LangChain) et yield chaque morceau de contenu au fur et à mesure.
- `agent/controller.py` : `stream_chat(session_id, user_message, user_id=None)`
  — variante streaming de `handle_chat`. Elle gère **sa propre session DB**
  (`SessionLocal()` directe) plutôt que `Depends(get_db)` : avec une réponse en
  streaming, FastAPI ferme les dépendances dès que la route retourne l'objet
  `StreamingResponse`, bien avant que le générateur ait fini de produire les
  morceaux et d'écrire la persistance finale (court terme, PostgreSQL, Chroma).
  L'utiliser aurait fermé la session avant la fin du flux.
- `STREAM_ERROR_MARKER` : si le LLM échoue *en cours* de streaming, les entêtes
  HTTP (200) sont déjà envoyés — impossible de renvoyer un vrai 502 à ce
  stade. L'échec est donc signalé par un marqueur dans le flux lui-même
  (`"\n\n<<JARVIS_STREAM_ERROR>>"`), que le frontend détecte et retire de
  l'affichage.
- `POST /chat/stream` (`api/routes/chat.py`) : `StreamingResponse` en
  `text/plain`, texte brut chunké (pas de vrai protocole SSE — inutile ici
  puisque backend et frontend sont les mêmes deux bouts que je contrôle).
- Frontend : `streamChatMessage()` (`lib/api.ts`) lit `response.body` via
  `ReadableStream`/`TextDecoder` et notifie l'appelant à chaque chunk.
  `ChatWindow.tsx` affiche soit les points "Jarvis réfléchit" (avant le
  premier chunk), soit une bulle qui grandit au fur et à mesure.
  L'ancien `/chat` (non-streaming) est conservé tel quel — toujours utilisé
  par les tests et disponible si besoin d'un appel simple.

## Vérifié

- Backend : 4 nouveaux tests (`tests/test_chat_stream.py`) — réponse complète
  reconstituée, persistance identique à `/chat`, marqueur d'erreur, validation
  422. Suite complète : 18 tests.
- Frontend : `tsc --noEmit` propre. Test réel dans un navigateur (Playwright)
  contre un faux backend local qui streame mot par mot avec un délai —
  captures d'écran confirmant : la bulle "réflexion" (points qui rebondissent)
  pendant la latence avant le premier morceau, puis la bulle qui grandit
  progressivement, puis le message final identique à un message normal.
