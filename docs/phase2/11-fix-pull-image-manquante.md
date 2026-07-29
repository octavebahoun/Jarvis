# 11 — Fix : image Docker manquante non téléchargée automatiquement

## Le bug (découvert en test réel, troisième vague)

Après les fixes réseau (doc 09) et imports (doc 10), le premier vrai test de
`code_executor` échoue :

```
404 Client Error for http+docker://localhost/v1.52/containers/create:
Not Found ("No such image: python:3.11-slim")
```

## Cause

`tools/_sandbox.py` utilise l'API bas niveau `client.containers.create()`.
Contrairement à `docker run` en CLI (ou à la méthode de confort
`client.containers.run()`), **`containers.create()` ne télécharge jamais une
image manquante** — il échoue immédiatement si elle n'est pas déjà présente
localement. `python:3.11-slim` n'avait jamais été pull sur la machine de
l'utilisateur.

## Le fix

`_ensure_image(client, image)` : vérifie la présence locale de l'image
(`client.images.get`) et la télécharge (`client.images.pull`) si absente
(`docker.errors.ImageNotFound`), avant `containers.create()`. Coût : un aller-
retour local rapide à chaque appel une fois l'image en cache (juste une
vérification, pas un re-téléchargement).

## Vérifié

2 tests (`test_sandbox.py`, client Docker simulé avec/sans image déjà
présente) : pas de pull si l'image existe, pull déclenché sinon. Suite
complète : 67 tests. Le comportement réel (téléchargement effectif de
`python:3.11-slim` et de l'image Playwright) reste à confirmer chez
l'utilisateur.
