# 17 — Dégradation gracieuse de la mémoire vectorielle

## Le problème (découvert en test réel sur Termux/Android)

Après le fix de logging (doc 16), le vrai bug suivant est apparu clairement :
sur une connexion mobile très lente, le téléchargement du modèle ONNX
(`EMBEDDING_PROVIDER=local`, ~80 Mo, voir doc 08) expirait
(`httpx.ReadTimeout`). Contrairement à l'appel LLM, **rien ne protégeait les
appels à `vector_store.search_memory` / `add_memory`** dans
`agent/controller.py` : une panne à cet endroit remontait telle quelle et
plantait toute la requête (`500 Exception in ASGI application`), y compris
sur `/chat` (pas seulement le flux streaming).

## Ce qui a été corrigé

`agent/controller.py` : `_safe_search_memory()` et `_safe_add_memory()`
enveloppent les deux appels à `vector_store`. En cas d'échec (Chroma
injoignable, téléchargement du modèle qui time-out, etc.), l'erreur est
loggée (`logger.exception`) et :
- `search_memory` renvoie une liste vide → le chat continue **sans contexte
  RAG** plutôt que d'échouer.
- `add_memory` échoue silencieusement (loggé) → l'échange a déjà une réponse
  valide à ce stade, pas de raison de faire échouer la requête pour un
  souvenir qui ne sera pas indexé.

C'est la même philosophie que la gestion de panne LLM (doc 07) : la mémoire
vectorielle est un enrichissement, pas une dépendance dure du chat.

## Vérifié

Deux tests ajoutés (`test_chat_degrades_gracefully_when_vector_search_fails`,
`..._when_vector_add_fails`) : `search_memory`/`add_memory` simulés en échec,
`/chat` renvoie quand même `200` avec la réponse attendue. Suite complète :
22 tests.

## Reste indépendant de ce fix

Le problème réseau lui-même (téléchargement du modèle ONNX trop lent sur
mobile) n'est pas "corrigé" par ce changement — il est simplement **absorbé
proprement** au lieu de faire planter le chat. La solution pratique reste de
pré-télécharger le modèle sur une connexion correcte (fichier mis en cache de
façon permanente une fois présent) ou de rester sur `EMBEDDING_PROVIDER=openai`
si le réseau local ne permet pas ce téléchargement initial.
