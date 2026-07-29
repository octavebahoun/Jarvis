# 04 — Dashboard : vue des automatisations

## Ce qui a été construit

Une page `/dashboard` qui liste les automatisations de l'utilisateur et
permet de les activer/désactiver, sans passer par `curl`.

Jusqu'ici, une automatisation n'était visible que :

- au moment de sa création, via la carte `AutomationCard` dans le fil du chat
  (une seule automatisation à la fois, celle qui vient d'être créée) ;
- ou en interrogeant l'API à la main (`GET /automations`).

Concrètement, une automatisation créée trois jours plus tôt devenait
invisible : impossible de savoir ce qui tournait encore, ni pourquoi. Le
scénario qui a motivé cette page est réel — plusieurs automatisations de test
créées pendant la validation manuelle sont restées `active: true` faute d'un
endroit pour les voir.

### Contenu de la page

Pour chaque automatisation :

- son nom et la tâche en langage naturel qui sera transmise au planner ;
- son cron **traduit en français** (« Tous les jours à 08:00 UTC »), avec
  l'expression brute conservée à côté ;
- l'heure locale équivalente, quand le cron fixe une heure précise ;
- le statut de la dernière exécution (`done` / `failed` / jamais exécutée) et
  sa date ;
- un bouton qui bascule active ↔ inactive.

Un compteur « N actives sur M » donne l'état global en un coup d'œil.

## Fichiers

| Fichier | Rôle |
| --- | --- |
| `frontend/app/dashboard/page.tsx` | Page : chargement, bascule, états vide/erreur |
| `frontend/components/AutomationRow.tsx` | Rendu d'une ligne (présentationnel) |
| `frontend/lib/cron.ts` | Traduction cron → français, indication d'heure locale |
| `frontend/lib/api.ts` | `listAutomations()`, `toggleAutomation()` |

## Décisions et pourquoi

### Aucun changement backend

`GET /automations` et `PUT /automations/:id/toggle` existaient déjà depuis
`01-scheduler-et-automatisations.md`. Cette évolution est donc purement
frontend : un commit court, facile à relire, facile à annuler.

Les deux autres blocs prévus pour le dashboard (mémoire long terme,
historique des plans) sont volontairement laissés de côté. L'historique
demandera une nouvelle route `GET /tasks` côté backend et sera traité à part.

### Le cron est traduit, jamais réécrit

`describeCron()` ne couvre que les formes courantes (quotidien,
hebdomadaire, mensuel, ponctuel, toutes les N minutes/heures). Toute
expression non reconnue est affichée **telle quelle**.

C'est délibéré : une paraphrase approximative d'un cron est pire que le cron
brut. Un utilisateur qui lit « Tous les jours à 08:00 » alors que
l'expression dit autre chose désactivera la mauvaise automatisation. Pour la
même raison, l'expression brute reste toujours visible à côté de la
traduction — elle est la source de vérité.

### L'heure locale est une indication, pas une traduction

Les crons sont évalués en UTC (`scheduler/registry.py`). La description reste
donc en UTC, et l'heure locale est ajoutée séparément (« ≈ 09:00 chez toi »).

Convertir aussi le **jour** ferait dériver le libellé d'un jour entier près
des bornes de minuit : `0 23 * * 1` (lundi 23h UTC) est un mardi à Cotonou.
Afficher « Tous les mardis » serait faux la moitié de l'année selon le
fuseau. Mieux vaut une heure locale indicative et un jour UTC exact.

`localTimeHint()` dépend du fuseau du navigateur : elle n'est appelée que
dans le rendu de la liste, qui n'existe qu'après le `fetch` côté client — pas
de divergence entre rendu serveur et rendu client.

### Bascule optimiste ciblée, pas de rechargement complet

`PUT /toggle` renvoie l'automatisation à jour. On remplace la ligne concernée
dans le tableau en mémoire plutôt que de relancer `GET /automations` : la
liste entière ne clignote pas pour un changement d'une seule ligne. Le bouton
est désactivé pendant l'aller-retour (`togglingId`) pour éviter les
double-clics, qui produiraient deux bascules et donc aucun changement visible.

### Chargement initial en promesse plutôt qu'en `async` appelée

La règle ESLint `react-hooks/set-state-in-effect` interdit d'appeler depuis un
`useEffect` une fonction qui met l'état à jour, y compris après un `await`.
Le chargement initial est donc écrit sous forme de `listAutomations().then()`
dans l'effet (avec un drapeau `cancelled`), et la fonction `load()` reste
réservée au bouton « Rafraîchir ». C'est le même motif que
`app/chat/page.tsx` et `components/AutomationCard.tsx`.

## Ce qui a été vérifié

- `npx tsc --noEmit` : aucune erreur de type.
- `npx eslint` sur les fichiers touchés : aucun avertissement.
- `npm run build` : la compilation aboutit ; seul le téléchargement des
  Google Fonts échoue, la politique réseau de l'environnement de
  développement le bloquant. À relancer sur une machine avec accès réseau
  avant merge.

Vérifications navigateur à faire à la main : voir la section « Dashboard »
de `docs/checklist-test-manuel.md`.

## Limites connues

- Pas de suppression d'automatisation (l'API n'expose pas de `DELETE`) :
  désactiver reste le seul moyen d'en arrêter une.
- Pas de création depuis le dashboard — cela passe par le chat en langage
  naturel (`02-pont-chat-vers-automatisation.md`) ou par `POST /automations`.
- Le statut affiché est celui de la **dernière** exécution seulement ;
  l'historique complet des exécutions viendra avec le bloc « historique des
  plans ».
- Pas de rafraîchissement automatique : une automatisation qui se déclenche
  pendant que la page est ouverte n'apparaît qu'après un clic sur
  « Rafraîchir ».
