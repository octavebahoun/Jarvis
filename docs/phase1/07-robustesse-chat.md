# 07 — Robustesse de l'endpoint /chat

## Ce qui a été construit

- **Validation d'entrée** : `ChatRequest.message` et `.session_id` refusent
  désormais les chaînes vides (`Field(min_length=1)`) → `422` au lieu de
  déclencher un appel LLM inutile avec un message vide.
- **Panne LLM gérée proprement** : `agent/controller.py` expose
  `AgentUnavailableError`, levée quand `reasoning.generate_reply()` échoue
  (clé OpenAI absente/invalide, service indisponible...). La route `/chat`
  la traduit en `HTTPException(502)` avec un message clair, plutôt que de
  laisser remonter un `500` générique avec une stack trace.

## Pourquoi maintenant

En testant l'API bout-en-bout (doc 04, 06), l'appel LLM est le seul point
externe vraiment susceptible d'échouer en usage réel (clé absente au premier
lancement, quota dépassé, réseau...). Une erreur claire à cet endroit est ce
qui distingue un "chat intelligent" utilisable d'un prototype qui crashe —
donc dans le scope de la Phase 1, pas une extension.

## Tests ajoutés

- `test_chat_rejects_empty_message` (422)
- `test_chat_returns_502_when_llm_unavailable` (502, LLM simulé en échec)

Suite complète (11 tests) revérifiée avec la même méthode que la doc 06.
