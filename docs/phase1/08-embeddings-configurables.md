# 08 — Provider d'embeddings configurable (OpenAI ↔ local)

## Ce qui a été construit

- `EMBEDDING_PROVIDER` (nouvelle variable d'env, `openai` par défaut ou
  `local`) dans `config.py`, plus `OPENAI_EMBEDDING_MODEL` (défaut
  `text-embedding-3-small`).
- `backend/memory/vector_store.py` :
  - `get_embedder()` retourne `OpenAIEmbeddings` ou `LocalEmbeddings` selon
    `settings.embedding_provider`, sans changer le reste du code (`add_memory`
    / `search_memory` ne savent pas quel provider est utilisé).
  - `LocalEmbeddings` : wrapper autour du modèle **MiniLM (ONNX)** déjà
    embarqué par ChromaDB (`chromadb.utils.embedding_functions.
    DefaultEmbeddingFunction`) — c'est le modèle local évoqué en discussion
    (`all-MiniLM-L6-v2`), mais servi via ONNX Runtime plutôt que
    `sentence-transformers`/PyTorch.
  - Les collections Chroma sont désormais nommées par provider
    (`jarvis_memory_openai` / `jarvis_memory_local`) : les deux modèles ne
    produisent pas des vecteurs de même dimension (1536 vs 384), donc changer
    de provider sur une collection existante aurait fait planter Chroma.
  - La collection est créée avec `hnsw:space: cosine` explicite (avant : valeur
    par défaut de Chroma, non garantie être la similarité cosinus documentée
    dans `phase1.md`).

## Pourquoi ONNX MiniLM plutôt que sentence-transformers

`sentence-transformers` embarque PyTorch (des centaines de Mo, temps
d'installation long). ChromaDB fournit déjà, en interne, le même modèle
(`all-MiniLM-L6-v2`) exporté en ONNX et exécuté via `onnxruntime` — package
**déjà présent** dans `requirements.txt` (utilisé par Chroma lui-même). Résultat
: le mode local marche sans ajouter une seule dépendance au projet, et sans
toucher `requirements.txt`.

## Comment basculer

```env
# .env
EMBEDDING_PROVIDER=local   # au lieu de "openai"
```

Aucun changement de code requis. Le modèle ONNX (~80 Mo) est téléchargé et mis
en cache par Chroma au premier appel (pas au démarrage de l'API), puis tourne
ensuite entièrement en local sur CPU, sans clé API ni coût.

## Vérifié dans ce tour

- `get_embedder()` bascule bien entre les deux implémentations selon
  `EMBEDDING_PROVIDER` (tests `tests/test_vector_store.py`).
- `LocalEmbeddings.embed_query()` exécuté réellement dans ce sandbox : le
  modèle ONNX se télécharge, et produit un vecteur de 384 dimensions.
- Suite complète (14 tests) revérifiée avec la même méthode que les docs 06/07.
