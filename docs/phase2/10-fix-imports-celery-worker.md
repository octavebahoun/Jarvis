# 10 — Fix : imports différés cassés dans le worker Celery

## Le bug (découvert en test réel, deuxième vague)

Après le fix réseau (doc 09), le worker démarre et se connecte bien à Redis,
mais la première tâche réelle plante :

```
Task tasks.execute_plan_task[...] raised unexpected: ModuleNotFoundError("No module named 'agent'")
  File "/app/tasks/worker.py", line 13, in _run_plan
    from agent.executor import execute_plan
```

Le plan reste bloqué : son statut passe bien à `approved` (l'appel HTTP a
réussi), mais l'étape ne progresse jamais côté worker.

## Cause

Celery (`-A tasks.worker.celery_app`) n'ajoute le répertoire courant à
`sys.path` que **temporairement**, le temps de charger le module de l'app
(`import_from_cwd`, qui utilise un context manager retirant ensuite ce chemin).
`tasks/worker.py` avait ses imports (`agent.executor`, `db.session`,
`tasks.task_store`) **à l'intérieur** de la fonction `_run_plan`, donc
jamais exécutés pendant le chargement initial du module — seulement plus
tard, à l'exécution réelle d'une tâche, une fois ce chemin retiré. `tasks`
lui-même s'importait sans problème (c'est justement le module en cours de
chargement par Celery à ce moment-là), ce qui a rendu le bug moins évident au
premier coup d'œil.

## Le fix

Les trois imports remontent au **niveau du module**, dans le bloc d'imports
en tête de `tasks/worker.py`, aux côtés de `from celery import Celery`. Ils
s'exécutent donc pendant la fenêtre où Celery a bien `/app` sur `sys.path`,
puis restent en cache dans `sys.modules` pour tous les workers forkés
ensuite. Comportement de `_run_plan()` inchangé, toujours testable sans
passer par la machinerie Celery.

## Pourquoi ce n'était pas testable avant

Les tests (`test_worker.py`) appellent `_run_plan()` directement depuis
`pytest`, où `sys.path` est déjà correctement configuré (`conftest.py` insère
`backend/` explicitement) — le bug ne se manifeste que dans le contexte
précis du chargement d'app par la CLI `celery`, jamais reproduit par les
tests automatisés ni par les scripts de simulation utilisés dans ce sandbox.
Seul un vrai `celery worker` en situation réelle le révèle.

## Vérifié

Suite complète (66 tests) revérifiée après le déplacement des imports —
aucune régression. Le comportement réel avec Celery reste à reconfirmer sur
la machine de l'utilisateur (c'est justement ce test qui a trouvé le bug).
