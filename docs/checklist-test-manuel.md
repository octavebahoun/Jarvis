# Checklist de test manuel — Phase 1 + Phase 2

Tests fonctionnels à faire toi-même dans le navigateur / terminal, en
complément de la suite `pytest` (automatisée, ne couvre pas l'expérience
utilisateur réelle ni Docker/Celery réels). Coche au fur et à mesure.

Prérequis : `docker compose up -d --build` (stack à jour, cf. fix réseau) +
`npm run dev` dans `frontend/`.

---

## Phase 1 — Chat, mémoire, profil

### Chat de base
- [ ] Ouvrir `/chat`, envoyer un message → la réponse arrive **en streaming**
      (le texte apparaît progressivement, pas d'un bloc)
- [ ] Pendant l'attente, avant le premier mot : les **points qui rebondissent**
      ("Jarvis réfléchit") s'affichent
- [ ] La réponse contient du **markdown** rendu (demande explicitement du gras,
      une liste, du code inline) → correctement formaté, pas de `**`/`` ` `` bruts
- [ ] Chaque message affiche une **heure** sous la bulle

### Persistance de session
- [ ] Envoyer 2-3 messages, **recharger la page** (F5) → l'historique
      réapparaît (pas de conversation vide)
- [ ] Cliquer **"Nouvelle conversation"** → l'historique se vide, un nouveau
      message part bien dans une session propre

### Erreurs différenciées
- [ ] Backend éteint (`docker compose stop backend`) puis envoyer un message
      → message **"Impossible de joindre Jarvis..."**
- [ ] Redémarrer le backend (`docker compose start backend`) avant de continuer

### Profil & mémoire long terme
- [ ] Cliquer **"Profil & mémoire"** → le panneau s'ouvre, affiche le profil
      (`default`) et la stack technique si renseignée
- [ ] Section "Mémoire long terme" : vide au départ (aucune route ne crée de
      fait automatiquement, normal — cf. doc phase1/12)

### Providers configurables (à tester en changeant `.env` + redémarrage)
- [ ] `EMBEDDING_PROVIDER=local` → le chat fonctionne toujours (le modèle
      MiniLM se télécharge au premier appel, visible dans les logs backend)
- [ ] `CHAT_PROVIDER=openrouter` avec une clé valide → le chat répond toujours

---

## Phase 2 — Agent, tools, plans

Pour chaque tool, vérifie le **cycle complet** : plan proposé (pending) →
"Approuver l'exécution" → statut passe à "En cours..." en temps réel
(WebSocket) → statut "Terminé" (ou "Échoué") avec résultat affiché.

### file_reader
- [ ] Déposer un fichier texte dans `./sandbox/` (racine du projet, monté
      dans les containers)
- [ ] Demander *"Lis le fichier `<nom>` et résume-le"* → plan avec l'étape
      `file_reader` → approuver → le contenu du fichier apparaît dans le
      résultat de l'étape
- [ ] Demander de lire un fichier **hors sandbox** (ex. chemin absolu type
      `/etc/passwd`) → doit échouer proprement (étape "Échoué"), jamais lire
      le vrai fichier

### web_search (si `TAVILY_API_KEY` configurée)
- [ ] *"Cherche les dernières nouvelles sur ..."* → plan avec `web_search` →
      approuver → des résultats (titres + liens) apparaissent

### code_executor (Docker réel)
- [ ] *"Exécute ce code Python : print(2 + 2)"* → plan avec `code_executor` →
      approuver → résultat = `4`
- [ ] Vérifier dans `docker compose logs -f worker` qu'un container éphémère
      est bien créé puis détruit (`docker ps` pendant l'exécution le montre
      brièvement)
- [ ] Code qui boucle à l'infini (`while True: pass`) → doit être **tué après
      le timeout** (10s par défaut), étape "Échoué", pas de container qui
      traîne (`docker ps -a` après coup)

### browser_automation (Playwright réel)
- [ ] *"Va sur https://example.com et dis-moi ce qu'il y a d'écrit"* → plan →
      approuver → le texte de la page extrait apparaît
- [ ] Avec un sélecteur précis si tu veux tester `selector` (ex. demander
      seulement le titre `h1`)

### Plans multi-étapes
- [ ] Demander quelque chose qui combine deux tools (ex. *"Cherche X sur le
      web puis résume le fichier Y"*) → plan avec **plusieurs étapes dans
      l'ordre**, exécutées une à une (vérifie que la 2ᵉ ne démarre qu'une
      fois la 1ʳᵉ "Terminé")

### Panne / robustesse
- [ ] Une étape qui échoue (ex. fichier inexistant en 1ère étape d'un plan à
      2 étapes) → le plan passe "Échoué", la **2ᵉ étape reste "pending"**
      (jamais exécutée)
- [ ] Couper Redis (`docker compose stop redis`) après avoir approuvé un plan
      → le worker ne peut plus se connecter (attendu, pas un bug) ;
      redémarrer Redis pour continuer

### Chat simple toujours fonctionnel
- [ ] Un message qui **ne nécessite aucun tool** (ex. *"Salut, ça va ?"*) →
      toujours traité comme du chat normal (Phase 1 intact), pas de plan
      proposé inutilement

---

## Phase 3 — Scheduler + automatisations

Prérequis : `docker compose build browser-sandbox-image` (si pas déjà fait) +
`docker compose up -d --build` (inclut désormais le service `beat`).

- [ ] `POST /automations` avec un schedule cron invalide (ex. `"pas un cron"`)
      → 422
- [ ] `POST /automations` avec `{"name": "Test", "schedule": "* * * * *",
      "task": "cherche les dernières nouvelles sur l'IA"}` (toutes les
      minutes, pour tester vite) → 200, `active: true`
- [ ] Dans `docker compose logs -f beat` : un tick `scheduler.tick` visible
      chaque minute
- [ ] Dans `docker compose logs -f worker` : dans la minute qui suit, la
      tâche s'exécute (le worker traite `scheduler.tick` puis lance le plan)
- [ ] `GET /automations` → `last_run_status: "done"`, `last_run_plan_id`
      renseigné, `last_run_at` mis à jour
- [ ] `GET /tasks/<last_run_plan_id>` → le plan est bien "done" avec un résumé
- [ ] `PUT /automations/:id/toggle` → `active: false` ; attendre une minute,
      vérifier qu'elle ne se relance plus (`last_run_at` ne change plus)
- [ ] Créer une automatisation dont la tâche pousse le planner vers un tool
      sensible (ex. *"exécute ce code Python : print(1)"*) → doit échouer
      proprement (`last_run_status: "failed"`), jamais s'auto-approuver
- [ ] Supprimer l'automatisation de test une fois les vérifications faites
      (pas de route DELETE pour l'instant — direct en base ou laisser
      `active: false`)

## Après le passage complet

Si tout est coché : la Phase 2 est validée de bout en bout avec la vraie
stack (critère de merge de `phase2.md`). Note ici ce qui a échoué, sinon on
corrige avant de considérer que c'est fini.
