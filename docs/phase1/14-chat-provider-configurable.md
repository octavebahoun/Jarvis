# 14 — Provider de chat configurable (OpenAI ↔ OpenRouter gratuit)

## Ce qui a été construit

Même logique que le provider d'embeddings (doc 08), appliquée au LLM du chat :

- `CHAT_PROVIDER` (config.py, `openai` par défaut ou `openrouter`) +
  `OPENROUTER_API_KEY`, `OPENROUTER_MODEL` (défaut
  `meta-llama/llama-3.1-8b-instruct:free`), `OPENROUTER_BASE_URL`.
- `agent/reasoning.py` : `_get_llm()` construit le `ChatOpenAI` selon le
  provider — OpenRouter expose une API compatible OpenAI, il suffit de
  changer `base_url` et `api_key`. `generate_reply()` et `stream_reply()`
  passent tous les deux par `_get_llm()`, donc le streaming (doc 10)
  fonctionne aussi bien avec OpenRouter qu'avec OpenAI, sans rien dupliquer.

## Comment basculer

```env
# .env
CHAT_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-...   # créée gratuitement sur openrouter.ai
```

Clé à créer sur [openrouter.ai](https://openrouter.ai) (compte gratuit). Les
modèles suffixés `:free` n'engagent aucun coût, avec des limites de débit plus
basses que les modèles payants — suffisant pour développer/tester sans clé
OpenAI. Le catalogue des modèles gratuits change dans le temps ; vérifier sur
openrouter.ai/models (filtre "free") si `OPENROUTER_MODEL` par défaut n'est
plus disponible.

## Point d'attention

`EMBEDDING_PROVIDER` et `CHAT_PROVIDER` sont **indépendants** : basculer le
chat sur OpenRouter ne change rien aux embeddings (toujours OpenAI par défaut,
ou `local` si configuré séparément, doc 08). OpenRouter n'est utilisé ici que
pour le LLM conversationnel.

## Vérifié

- `tests/test_reasoning.py` : `_get_llm()` bascule correctement entre les deux
  configurations (modèle et `base_url` corrects).
- Suite complète : 20 tests.
