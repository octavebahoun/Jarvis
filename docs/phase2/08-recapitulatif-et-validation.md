# 08 — Récapitulatif Phase 2 et validation réelle à faire

## Ce qui est fait

| Bloc | Contenu | Statut |
|---|---|---|
| 1 | Tool System (infra) + `file_reader` | ✅ testé |
| 2 | Tool `web_search` (Tavily) | ✅ testé |
| 3 | Modèles `Plan`/`PlanStep` + `planner.py` | ✅ testé |
| 4 | `executor.py` | ✅ testé |
| 5 | Tools sandboxés Docker (`code_executor`, `browser_automation`/Playwright) | ⚠️ Docker simulé uniquement |
| 6 | Queue Celery + API `/tasks` + WebSocket + `/chat` propose des plans | ⚠️ Celery/Redis simulés uniquement |
| 7 | Frontend (`PlanViewer`, `ToolCallCard`, `TaskStatus`) | ✅ testé en navigateur (backend simulé) |

66 tests backend, tous passants. Flux complet (proposition de plan →
approbation → exécution → suivi temps réel → résultat) vérifié en navigateur
réel, mais avec Docker/Celery/Redis **simulés** (aucun de ces services n'est
disponible dans ce sandbox).

## Ce qui reste à valider sur ta machine (Docker disponible)

C'est la dernière étape avant de considérer la Phase 2 mergeable, conforme au
critère explicite de `phase2.md` : *"Pas de merge sur main sans test
end-to-end du flux plan → validation → exécution."*

```bash
git pull origin claude/projet-anonyme-ch2wyx

# Lancer toute la stack, y compris le nouveau service worker
docker-compose up -d --build

# Vérifier que le worker Celery a bien démarré
docker-compose logs -f worker
```

### Test 1 — code_executor (Docker réel)

Envoie un message qui devrait déclencher `code_executor`, par exemple :
*"Exécute ce code Python : print(2 + 2)"*. Vérifie que :
- un plan apparaît avec l'étape `code_executor`
- après approbation, le statut passe à "En cours..." puis "Terminé"
- le résultat affiché est bien `4`

### Test 2 — browser_automation (Playwright réel)

Message du type : *"Va sur https://example.com et dis-moi ce qu'il y a d'écrit"*.
Vérifie que le contenu de la page est bien extrait et affiché.

### Points d'attention si ça ne marche pas du premier coup

- **`docker.errors.DockerException` / permission refusée** : le backend (hors
  container) doit avoir accès au socket Docker de l'hôte
  (`/var/run/docker.sock`) — si tu lances le backend directement (pas via
  `docker-compose`), vérifie que ton utilisateur est dans le groupe `docker`.
- **Image Playwright introuvable** : `BROWSER_AUTOMATION_IMAGE` pointe vers
  `mcr.microsoft.com/playwright/python:v1.49.0-noble` — si ce tag n'existe
  plus, ajuste la variable d'env vers un tag disponible
  (`docker pull mcr.microsoft.com/playwright/python` sans tag pour voir les
  options, ou la page Microsoft Container Registry).
- **Le worker ne semble rien exécuter** : vérifie `docker-compose logs worker`
  — la commande lancée est `celery -A tasks.worker.celery_app worker`.
- **Timeout systématique sur `code_executor`** : `CODE_EXECUTOR_TIMEOUT_SECONDS`
  (10s par défaut) peut être trop court si l'image `python:3.11-slim` doit
  encore être téléchargée la première fois — relance une fois l'image en cache.

Dis-moi ce que ça donne : si tout passe, la Phase 2 (dans son état actuel) est
validée de bout en bout. Il restera ensuite, si tu veux, à enrichir
(reject de plan, retry sur échec, plus de tools...) mais ce n'était pas dans
le plan initial.
