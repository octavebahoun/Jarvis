# 01 — Scheduler proactif + automatisations (première brique de Phase 3)

## Objectif de cette évolution

Poser le socle de Phase 3 avant d'attaquer les intégrations externes
(GitHub, Notion, Calendar — nécessitent OAuth, hors scope ici) ou le
dashboard : un mécanisme complet **déclencheur cron → plan → exécution →
journal**, sans validation humaine, réutilisant au maximum ce qui existe déjà
en Phase 2.

## Ce qui a été construit

- **Modèle `Automation`** (`db/models.py` + migration `3843ef374375`) : `name`,
  `schedule` (cron), `task` (objectif en langage naturel), `active`,
  `last_run_at`, `last_run_status`, `last_run_plan_id`.
- **`tasks/automation_store.py`** : CRUD, même pattern que `tasks/task_store.py`.
- **`agent/proactive.py`** (`run_automation`) : transmet `automation.task` au
  **même planner** que le chat (`agent/planner.build_plan`), auto-approuve le
  plan obtenu puis l'exécute avec le **même executor** que Phase 2
  (`agent/executor.execute_plan`) — aucune logique d'exécution dupliquée,
  conformément à la règle d'architecture de `phase3.md`
  ("`proactive.py` utilise les mêmes tools que `executor.py`").
- **Garde-fou sécurité** : si le plan proposé contient une étape dont le tool
  a `requires_validation=True` (`code_executor`, `browser_automation`),
  `run_automation` refuse d'exécuter — jamais d'auto-approbation d'un tool
  sensible. C'est la traduction concrète de la règle de `phase3.md` :
  *"les automatisations proactives ne peuvent pas exécuter code_executor sans
  session active de l'utilisateur"*, généralisée à tout tool marqué sensible
  (le même signal `requires_validation` qui protège déjà le flux Phase 2).
- **`scheduler/registry.py`** (`due_automations`) : sélectionne les
  automatisations actives dont l'expression cron matche la minute courante
  (librairie `croniter`).
- **`scheduler/jobs.py`** (tâche Celery `scheduler.tick`) : appelle
  `registry.due_automations` puis `proactive.run_automation` pour chacune —
  ne contient aucune logique métier, conformément à `phase3.md`.
- **Celery Beat** (`tasks/worker.py`, `celery_app.conf.beat_schedule`) :
  déclenche `scheduler.tick` chaque minute. Un seul tick générique plutôt
  qu'une entrée `beat_schedule` par automatisation : créer/activer une
  automatisation via l'API n'exige donc pas de redémarrer Beat.
- **`docker-compose.yml`** : nouveau service `beat`
  (`celery ... beat`) — publie les tâches sur Redis, c'est toujours le
  service `worker` existant qui les exécute réellement.
- **API** (`api/routes/automations.py`) : `POST /automations` (schedule
  validé via `croniter.is_valid`, 422 sinon), `GET /automations`,
  `PUT /automations/:id/toggle`.

## Décisions et pourquoi

- **Celery Beat plutôt qu'APScheduler** (proposé en alternative dans
  `phase3.md`) : Celery/Redis sont déjà en place depuis Phase 2, ajouter un
  second système de scheduling aurait été une duplication d'infrastructure
  sans bénéfice.
- **Poller générique (tick chaque minute) plutôt qu'un schedule Beat par
  automatisation** : Beat ne recharge sa config qu'au redémarrage — un
  schedule dynamique par automatisation aurait obligé à redémarrer le
  service à chaque création/modification. Le coût (une requête DB par
  minute) est négligeable au volume attendu.
- **`croniter`** : léger, `croniter.match(expr, dt)` couvre exactement le
  besoin (est-ce que cette expression matche cette minute précise) sans
  réimplémenter un parseur cron.
- **Automation.task en langage naturel, passé au planner** (plutôt qu'un
  tool+args figés dans le modèle) : cohérent avec l'exemple de `phase3.md`
  (`"task": "résumer les PRs et issues ouvertes"`), et réutilise
  intégralement le planner de Phase 2 sans nouveau code de décision.

## Ce qui n'est PAS fait dans cette évolution (volontairement)

Phase 3 est large (spec : 4-6 mois) — cette évolution pose seulement le
socle scheduler + automatisations, testable de bout en bout sans dépendance
externe :

- Pas d'intégrations externes (`tools/github.py`, `notion.py`,
  `calendar.py`) ni d'OAuth — nécessitent une automatisation utilisable dès
  maintenant avec les tools Phase 2 existants (`web_search`, `file_reader`)
  pour valider le mécanisme avant d'ajouter la complexité OAuth.
- Pas de dashboard frontend, pas de `/dashboard/summary` ni `/history`.
- Pas de suppression d'automatisation (seulement create/list/toggle, comme
  demandé par `phase3.md`) ni de limite de 10 automatisations actives
  (MVP — à ajouter si ça devient un vrai besoin).

## Vérifié

Migration testée par autogénération contre une base neuve (SQLite local,
zéro écart résiduel confirmé par une seconde autogénération à vide — même
méthode que la baseline Alembic, doc phase2/13). Import circulaire
`tasks.worker` ↔ `scheduler.jobs` vérifié dans les deux sens d'import.
Suite pytest complète (nouveaux tests `test_automation_store.py`,
`test_proactive.py`, `test_scheduler_registry.py`, `test_scheduler_jobs.py`,
`test_automations_routes.py` + suite existante) : verte contre un substitut
SQLite (pas de Postgres/Redis réels dans ce sandbox, limitation déjà
documentée). `docker compose config` valide la syntaxe du nouveau service
`beat`. Reste à confirmer par l'utilisateur en conditions réelles : le tick
Celery Beat toutes les minutes, et qu'une automatisation créée via l'API
s'exécute bien au moment prévu.
