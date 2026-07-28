# 02 — Système de mémoire

## Ce qui a été construit

- `backend/memory/short_term.py` : historique de conversation dans Redis.
  Clé `session:{session_id}:history`, liste de messages `{role, content}`
  (poussés avec `RPUSH`), TTL glissant de 2h (`short_term_ttl_seconds`,
  conforme à `phase1.md`) réappliqué à chaque nouveau message.
- `backend/memory/long_term.py` : CRUD simple sur la table `Fact` (ajout et
  liste des faits par utilisateur).
- `backend/memory/vector_store.py` : mémoire vectorielle via ChromaDB
  (`HttpClient` vers le service `chroma` du docker-compose). Les embeddings
  sont calculés côté application avec `OpenAIEmbeddings`
  (`text-embedding-3-small`) plutôt que par une fonction d'embedding interne à
  Chroma, pour n'avoir qu'une seule source de vérité sur la clé OpenAI et le
  modèle utilisé. `search_memory()` fait une recherche par similarité cosinus
  filtrée par `user_id`.

## Décisions

- **Pas d'extraction automatique de faits.** `long_term.py` expose juste
  `add_fact`/`list_facts` : rien n'analyse encore la conversation pour en
  extraire des faits durables tout seul. C'est une fonctionnalité à part entière
  (résumé + extraction via LLM) que la Phase 1 ("chat + mémoire + profil") ne
  demande pas explicitement — on l'ajoutera si l'usage réel du chat le justifie,
  plutôt que de la construire par anticipation.
- **Chaque échange va aussi dans le vector store.** Après une réponse de
  l'agent, le controller (voir doc 03) indexe la paire question/réponse dans
  Chroma. C'est ce qui permet la "recherche sémantique" demandée par la Phase 1
  sans dépendre uniquement des faits explicitement enregistrés.

## État

Le module s'importe et se comporte correctement (testé avec Redis simulé —
`fakeredis` — dans le sandbox, qui n'a pas Docker). Le comportement réel avec
Redis/Chroma sera à vérifier une fois `docker-compose up` lancé sur une machine
avec Docker actif.
