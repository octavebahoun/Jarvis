# 14 — Fix : course entre migrations concurrentes (backend / worker)

## Le problème (découvert en test réel, cinquième vague)

Après le passage à Alembic (doc 13), premier `docker compose down -v` +
`up -d --build` sur une base neuve : le service `backend` plante au
démarrage.

```
postgres-1  | ERROR:  duplicate key value violates unique constraint "pg_type_typname_nsp_index"
postgres-1  | DETAIL:  Key (typname, typnamespace)=(alembic_version, 2200) already exists.
backend-1   | sqlalchemy.exc.IntegrityError: ... CREATE TABLE alembic_version (...)
backend-1 exited with code 1
```

Le worker, lui, a réussi sa migration juste avant (`Running upgrade  ->
ea1f433822c9, baseline schema`).

## Cause

`backend` et `worker` exécutaient chacun `alembic upgrade head` dans leur
commande de démarrage. La doc 13 supposait que c'était sans risque car
« idempotent » — vrai en séquentiel, faux en parallèle. Sur une base neuve,
les deux containers démarrent en même temps : Alembic vérifie que la table
`alembic_version` n'existe pas (`checkfirst`) puis la crée — ce
check-then-create n'est pas atomique. Les deux process passent le check en
même temps, puis se battent pour le `CREATE TABLE` : le perdant plante avec
une violation de contrainte unique.

## Correctif

Isoler la migration dans un service dédié qui ne tourne qu'une fois, avant
que `backend` et `worker` ne démarrent :

- `docker-compose.yml` : nouveau service `migrate` (même image que
  `backend`), commande `alembic upgrade head`, `depends_on: postgres`
  (`condition: service_healthy` — d'où l'ajout d'un `healthcheck`
  `pg_isready` sur `postgres`, absent jusqu'ici).
- `backend` et `worker` : `depends_on: migrate` (`condition:
  service_completed_successfully`) — ils ne démarrent qu'une fois la
  migration terminée avec succès.
- `backend/dockerfile` : la commande de démarrage redevient uniquement
  `uvicorn ...` (la migration ne s'y fait plus).
- `worker` : commande redevenue uniquement `celery ... worker`.

## Vérifié

`docker compose config` valide la syntaxe (le sandbox n'a pas de daemon
Docker actif pour un test de démarrage réel — cf. limitation documentée dans
le résumé de session). Suite pytest inchangée (aucun code Python modifié,
uniquement l'orchestration Compose). Reste à confirmer par l'utilisateur sur
sa machine : `docker compose down -v && docker compose up -d --build`
devrait maintenant appliquer la migration une seule fois, proprement, avant
que `backend`/`worker` ne démarrent.
