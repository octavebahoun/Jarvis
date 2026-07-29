# 13 — Migrations Alembic (remplace create_all pour les changements de schéma)

## Le problème (découvert en test réel, quatrième vague)

Après l'ajout de `Plan.summary` (doc 12), le premier vrai test sur la machine
de l'utilisateur plante :

```
psycopg2.errors.UndefinedColumn: column "summary" of relation "plans" does not exist
```

Cause : `init_db()` (`db/session.py`) utilise `Base.metadata.create_all()`,
qui crée les tables **manquantes** mais n'altère **jamais** une table déjà
existante. La table `plans` de l'utilisateur avait été créée par une
précédente exécution (avant l'ajout de `summary`) — la nouvelle colonne n'a
donc jamais été ajoutée à la vraie base Postgres. C'est exactement le
scénario que la doc `phase1/01-...` anticipait : *"Alembic sera introduit dès
qu'on aura une première migration réelle à verser"*.

## Ce qui a été mis en place

- `backend/alembic/` (`env.py`, `script.py.mako`, `versions/`) +
  `backend/alembic.ini`.
- `alembic/env.py` : `target_metadata = Base.metadata` (import de
  `db.models` pour enregistrer tous les modèles), et `DATABASE_URL` lu
  dynamiquement depuis `config.get_settings()` plutôt qu'une valeur figée
  dans `alembic.ini` — cohérent avec la surcharge Docker Compose (doc 09).
- **Migration baseline** (`versions/ea1f433822c9_baseline_schema.py`) :
  générée par autogénération contre une base vide, capture l'état complet
  actuel des modèles (5 tables, tous les index, `Plan.summary` inclus).
  Vérifié : ré-exécuter l'autogénération après application de cette baseline
  ne détecte plus aucun écart.
- `dockerfile` : la commande de démarrage devient
  `alembic upgrade head && uvicorn ...` — la base est toujours mise à jour
  avant que l'API ne démarre.
- `docker-compose.yml` : le service `worker` applique aussi les migrations
  avant de lancer Celery (`depends_on` n'attend que le démarrage du
  container `backend`, pas la fin de sa commande — `alembic upgrade head`
  étant idempotent, l'exécuter deux fois ne pose pas de problème).

## Ce qui ne change pas

`init_db()` (`create_all()`) reste utilisé par les **tests** (bases SQLite
neuves à chaque run — jamais de dérive à corriger) et reste appelé au
démarrage de l'API comme filet de sécurité pour une base réellement vierge ;
il ne fait plus référence pour les changements de schéma sur une base déjà
initialisée, c'est le rôle d'Alembic désormais.

## À partir de maintenant

Après **tout** changement de `backend/db/models.py` :

```bash
alembic revision --autogenerate -m "description du changement"
alembic upgrade head
```

## Vérifié

Suite complète (69 tests) inchangée. Migration baseline testée : génération
contre base vide, application (`upgrade head`), re-génération confirmant zéro
écart résiduel. Le cas réel (base Postgres existante de l'utilisateur,
incomplète) nécessite un choix de sa part — recréer la base
(`docker compose down -v`) est la voie la plus simple pour repartir propre
avec Alembic dès maintenant.
