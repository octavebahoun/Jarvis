# 01 — Tool System (infrastructure) + premier tool (file_reader)

## Ce qui a été construit

- `backend/tools/__init__.py` : classe abstraite `BaseTool` (`name`,
  `description`, `requires_validation`, `run()`), registre **statique**
  (`list_tools()`, `get_tool(name)`) — conforme à la règle de `phase2.md`
  ("pas de chargement dynamique").
- `backend/tools/file_reader.py` : premier tool, lecture seule
  (`requires_validation = False`). Restreint strictement à `SANDBOX_PATH`
  (nouvelle variable de config) via `_resolve_safe_path()` : résout le chemin
  demandé, vérifie qu'il reste **dans** le sandbox (`Path.is_relative_to`),
  refuse sinon (`ValueError`) — protège contre la traversée de répertoire
  (`../../etc/passwd`) et les chemins absolus.

## Décisions

- **`BaseTool` vit dans `tools/__init__.py`**, pas dans un fichier séparé
  (`tools/base.py`) : l'arborescence documentée dans `phase2.md` ne prévoit
  que `__init__.py` + un fichier par tool. Un import circulaire est évité en
  définissant `BaseTool` *avant* d'importer les modules de tools individuels
  dans `__init__.py` (chaque tool fait `from tools import BaseTool`).
- **Ordre d'implémentation réajusté** par rapport à la présentation initiale :
  l'infra Tool System + un premier tool passent avant le planner, parce que
  le planner a besoin d'un registre de tools réel pour savoir quoi proposer
  au LLM.

## Vérifié

9 tests (`tests/test_tools_registry.py`, `tests/test_file_reader.py`) :
enregistrement du tool, erreur sur tool inconnu, lecture de fichier (racine et
sous-dossier), rejet d'une tentative de traversée (`../secret.txt`) et d'un
chemin absolu (`/etc/passwd`), erreur sur fichier manquant. Suite complète :
30 tests.
