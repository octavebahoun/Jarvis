# 12 — Panneau Profil & mémoire long terme

## Ce qui a été construit

- `lib/api.ts` : `getLongTermMemory()`, appelle `GET /memory?type=long_term`
  (route déjà existante, jamais utilisée côté frontend jusqu'ici).
- `components/MemoryPanel.tsx` : affiche le profil (nom, stack technique) et
  la liste des faits long terme. C'est le `MemoryPanel.tsx` prévu par
  `architecture.md` ("Visualisation mémoire (optionnel MVP)"), resté non
  implémenté jusqu'à maintenant.
- `app/chat/page.tsx` : bouton "Profil & mémoire" dans l'en-tête qui
  affiche/masque le panneau (repliable, pas de route dédiée).

## Décision : lecture seule

Le panneau n'ajoute **aucune** capacité d'écriture (pas de bouton "ajouter un
fait") : `backend/api/routes/memory.py` n'expose que `GET`, et rien dans
`agent/controller.py` n'appelle `long_term.add_fact()` automatiquement — les
faits ne peuvent aujourd'hui être créés que par du code Python direct (voir
comment j'ai peuplé les données de test ci-dessous). Ajouter une route
`POST /memory` et une UI pour créer des faits serait une vraie fonctionnalité
(extraction ou saisie manuelle de faits), pas juste de l'affichage — hors
scope de cette demande, qui portait sur "rendre visible ce qui existe déjà".

## Vérifié

`tsc --noEmit` propre. Test réel en navigateur avec un backend local dont le
profil et deux faits ont été peuplés directement en base (pas via l'API,
puisqu'aucune route de création n'existe) : le panneau affiche correctement
le nom, la stack technique (badges) et les deux faits.
