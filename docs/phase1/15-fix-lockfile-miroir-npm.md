# 15 — Correction définitive du miroir npm dans package-lock.json

## Le problème

Repéré lors de l'installation frontend dans ce sandbox (voir historique de la
session) : `frontend/package-lock.json` enregistrait les champs `resolved` de
764 paquets sur 844 vers `registry.npmmirror.com` (miroir chinois), au lieu du
registre npm officiel. Sur ce sandbox, un proxy bloque ce host (403), ce qui
faisait échouer ou traîner `npm install` en boucle avant d'abandonner.

Un premier contournement (`npm install --replace-registry-host=always`)
n'avait corrigé le problème que pour l'installation locale de la session, pas
pour le fichier commité : la question directe de l'utilisateur ("tu as
corrigé le problème... ?") a révélé que non, ce n'était pas réellement réglé.

## Pourquoi la première tentative de fix n'avait pas suffi

Supprimer `package-lock.json` et relancer `npm install --replace-registry-host=always`
ne suffisait pas : `node_modules` existant déjà et le cache npm local
(`~/.npm/_cacache`) contenant encore les métadonnées de paquets récupérées
via `registry.npmmirror.com` lors d'une session précédente, npm régénérait le
lockfile à partir de ces informations mises en cache plutôt que d'aller
chercher des données fraîches. Il a fallu :

```bash
rm -rf node_modules package-lock.json
npm cache clean --force
npm install --replace-registry-host=always
```

Après ce nettoyage complet du cache, la résolution s'est faite entièrement
via `registry.npmjs.org` (déjà la valeur de `npm config get registry` dans cet
environnement) : **0** occurrence de `registry.npmmirror.com` dans le nouveau
`package-lock.json` (817 entrées `resolved`, toutes vers npmjs.org).

## Vérifié

`tsc --noEmit`, `npm run lint`, `npm run build` (production) et un test réel
en navigateur (`/` et `/chat`) après cette réinstallation complète : tout
fonctionne à l'identique. Le nombre de paquets installés diffère légèrement
(dépendances optionnelles liées à la plateforme, normal lors d'une résolution
fraîche), sans impact fonctionnel.

## Portée de la correction

Ce correctif ne concerne que **ce sandbox** (proxy qui bloque
`registry.npmmirror.com`) — sur une machine avec un accès réseau normal, les
deux hosts fonctionnent. Mais avoir un lockfile pointant uniquement vers le
registre npm officiel est de toute façon plus portable (pas de dépendance à un
miroir tiers), donc ce changement reste correct à committer indépendamment du
contexte qui l'a révélé.
