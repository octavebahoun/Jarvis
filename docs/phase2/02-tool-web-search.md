# 02 — Tool web_search (Tavily)

## Ce qui a été construit

- `backend/tools/web_search.py` : `WebSearchTool`, `requires_validation = False`
  (recherche en lecture seule, pas d'effet de bord). Appelle l'API Tavily
  (`POST https://api.tavily.com/search`) directement via `httpx` — pas de SDK
  `tavily-python` ajouté, pour éviter une dépendance de plus alors qu'un
  simple appel HTTP suffit (`httpx` est déjà une dépendance du projet).
- `TAVILY_API_KEY` ajoutée à la config et aux `.env.example`.
- Enregistré dans le registre (`tools/__init__.py`).

## Pourquoi Tavily plutôt que Serper

Choix fait avec l'utilisateur : Tavily est pensé pour les agents IA (réponses
déjà résumées/nettoyées, pas du HTML de SERP brut à reparser), avec un quota
gratuit récurrent (1000 recherches/mois) plutôt qu'un crédit unique à
l'inscription.

## Vérifié

3 tests (`tests/test_web_search.py`), `httpx.post` simulé (aucun appel réseau
réel, aucune clé API nécessaire pour les tests) : formatage des résultats,
cas "aucun résultat", propagation d'une erreur amont (ex. clé invalide).
Suite complète : 33 tests.
