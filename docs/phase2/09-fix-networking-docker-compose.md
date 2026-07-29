# 09 — Fix : réseau Docker Compose (localhost vs noms de service)

## Le bug (découvert en test réel)

Premier vrai test avec `docker-compose up` sur la machine de l'utilisateur :
le worker Celery boucle en erreur `Cannot connect to redis://localhost:6379/1:
Connection refused`.

Cause : `.env.example` (et donc `.env`) définit `DATABASE_URL`, `REDIS_URL`,
`CHROMA_HOST`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` avec `localhost` —
correct quand le backend tourne **directement sur l'hôte** (le cas testé tout
au long des Phases 1 et 2 dans ce sandbox, faute de daemon Docker
disponible), mais faux quand le backend/worker tournent **eux-mêmes dans des
containers** : depuis l'intérieur du container `worker`, `localhost` désigne
le container lui-même, pas le container `redis` voisin. Il faut le nom du
service Docker Compose (`redis`, `postgres`, `chroma`).

Ce point n'avait jamais pu être testé avant : ce sandbox n'a pas de daemon
Docker actif, donc `docker-compose up` complet n'avait encore jamais tourné
réellement — seulement des simulations (fakeredis, SQLite, client Docker
mocké).

## Le fix

`docker-compose.yml` : les services `backend` et `worker` gardent
`env_file: .env` (clés API, secrets...) mais ajoutent un bloc `environment:`
qui **surcharge** spécifiquement les URLs réseau avec les noms de service :

```yaml
environment:
  DATABASE_URL: postgresql://jarvis:jarvis@postgres:5432/jarvis
  REDIS_URL: redis://redis:6379
  CHROMA_HOST: chroma
  CELERY_BROKER_URL: redis://redis:6379/1
  CELERY_RESULT_BACKEND: redis://redis:6379/2
```

Docker Compose applique `env_file` puis `environment:` par-dessus : les clés
qui apparaissent dans les deux prennent la valeur de `environment:`. Le même
`.env` reste valable pour un lancement direct sur l'hôte (backend/tests en
dehors de Docker) **et** pour `docker-compose up` (grâce à cette surcharge).

## Vérifié

`docker compose config` (validation statique, sans daemon) confirme que les
5 variables réseau résolvent bien vers les noms de service dans les deux
containers concernés. Le comportement réel (connexion effective) reste à
confirmer par l'utilisateur — c'est justement ce test qui a révélé le bug.
