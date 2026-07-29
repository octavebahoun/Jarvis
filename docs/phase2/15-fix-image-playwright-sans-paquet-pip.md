# 15 — Fix : l'image Playwright officielle n'embarque pas le paquet pip

## Le problème (découvert en test réel, sixième vague)

Premier test réel de `browser_automation` (après téléchargement manuel de
l'image `mcr.microsoft.com/playwright/python:v1.49.0-noble`) : le plan
échoue à l'étape `browser_automation`.

```
Traceback (most recent call last):
  File "<string>", line 2, in <module>
ModuleNotFoundError: No module named 'playwright'
```

## Cause

L'image officielle `mcr.microsoft.com/playwright/python` fournit les
navigateurs (Chromium/Firefox/WebKit) et leurs dépendances système, mais
**pas** le paquet pip `playwright` lui-même — hypothèse erronée lors du choix
initial de cette image (doc 05). Confirmé par les retours d'utilisateurs du
projet Playwright sur ce même piège
([microsoft/playwright#34872](https://github.com/microsoft/playwright/issues/34872),
[microsoft/playwright-python#2086](https://github.com/microsoft/playwright-python/issues/2086)).

## Correctif

Construire une image maison, dérivée de l'officielle, qui installe le paquet
pip à la version exacte des navigateurs embarqués (Playwright est strict sur
cette correspondance) :

- `docker/playwright-sandbox.dockerfile` : `FROM
  mcr.microsoft.com/playwright/python:v1.49.0-noble` + `pip install
  playwright==1.49.0`.
- `docker-compose.yml` : nouveau service `browser-sandbox-image`, avec
  `profiles: ["build-only"]` pour ne jamais démarrer via un `up` normal — il
  sert uniquement à builder/tagger l'image (`jarvis-playwright-sandbox:v1.49.0`)
  via `docker compose build browser-sandbox-image`.
- `config.py` / `.env.example` : `BROWSER_AUTOMATION_IMAGE` pointe désormais
  vers cette image maison plutôt que l'officielle brute.

## À partir de maintenant

Après un `git pull` qui touche ce fichier, ou sur une machine neuve : builder
l'image une fois avant le premier test de `browser_automation` :

```bash
docker compose build browser-sandbox-image
```

`_ensure_image()` (`tools/_sandbox.py`) réutilisera ensuite cette image en
cache local à chaque exécution du tool, sans re-build ni pull (elle n'est sur
aucun registre).

## Vérifié

`docker compose config` valide la syntaxe (pas de daemon Docker actif dans ce
sandbox pour un build réel). Aucun code Python modifié en dehors de la valeur
par défaut de `browser_automation_image` — suite pytest inchangée. Reste à
confirmer par l'utilisateur sur sa machine.
