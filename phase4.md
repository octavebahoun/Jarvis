# 🔴 Double Numérique Intelligent — Phase 4 : Jarvis-like

> L'agent anticipe, parle, entend, et contrôle le système. Version finale.

---

## 📌 Objectif Phase 4

Atteindre le niveau d'un **assistant personnel autonome** capable de :
- Communiquer vocalement (voix entrée + sortie)
- Contrôler le système d'exploitation (fichiers, apps, OS)
- Anticiper les besoins sans attendre d'être interrogé
- Coordonner plusieurs agents spécialisés en parallèle

**Prérequis :** Phase 3 stable — Dashboard + Automatisations opérationnels.

---

## ⚙️ Stack — Ajouts Phase 4

| Couche | Technologie | Rôle |
|--------|-------------|------|
| Speech-to-Text | OpenAI Whisper | Transcription voix → texte |
| Text-to-Speech | ElevenLabs / OpenAI TTS | Synthèse voix naturelle |
| Contrôle OS | pyautogui + subprocess | Actions clavier/souris/système |
| Multi-agents | LangChain Multi-Agent / CrewAI | Agents spécialisés en parallèle |
| Modèle local | Ollama + Mistral / LLaMA 3 | Traitement offline, données sensibles |
| Desktop app | Tauri (Rust + React) | App desktop native (optionnel) |

> Tout le reste est hérité des Phases 1, 2 et 3.

---

## 🗂️ Nouveaux fichiers

```
jarvis/
│
├── backend/
│   ├── voice/
│   │   ├── listener.py          # 🆕 Capture micro → transcription Whisper
│   │   ├── speaker.py           # 🆕 Texte → synthèse vocale
│   │   └── wake_word.py         # 🆕 Détection mot de réveil ("Hey Jarvis")
│   │
│   ├── os_control/
│   │   ├── file_system.py       # 🆕 Création / déplacement / suppression fichiers
│   │   ├── app_launcher.py      # 🆕 Ouvrir / fermer des applications
│   │   └── screen_reader.py     # 🆕 Lire le contenu de l'écran (OCR)
│   │
│   ├── multi_agent/
│   │   ├── orchestrator.py      # 🆕 Distribue les tâches entre agents
│   │   ├── agents/
│   │   │   ├── dev_agent.py     # 🆕 Spécialisé : code, debug, architecture
│   │   │   ├── research_agent.py# 🆕 Spécialisé : veille, recherche, synthèse
│   │   │   └── coach_agent.py   # 🆕 Spécialisé : apprentissage, progression
│   │
│   ├── anticipation/
│   │   └── predictor.py         # 🆕 Analyse patterns → suggestions proactives
│   │
│   └── local_llm/
│       └── ollama_client.py     # 🆕 Interface vers modèle local Ollama
│
├── frontend/
│   └── components/
│       ├── VoiceButton.tsx      # 🆕 Bouton micro + visualisation audio
│       └── AgentStatus.tsx      # 🆕 Statut des agents actifs en parallèle
│
└── desktop/                     # 🆕 App Tauri (optionnel)
    ├── src-tauri/
    └── src/
```

---

## 🔄 Flux vocal

```
[Utilisateur parle]
    ↓
wake_word.py → détecte "Hey Jarvis"
    ↓
listener.py → capture audio → Whisper → texte
    ↓
controller.py (Phase 1-3) → traitement normal
    ↓
réponse texte → speaker.py → ElevenLabs → audio
    ↓
[Jarvis répond à voix haute]
```

---

## 🔄 Flux multi-agents

```
Tâche complexe détectée (ex: "Prépare ma semaine")
    ↓
orchestrator.py → décompose par domaine
    ├── dev_agent     → résume les PRs GitHub en attente
    ├── research_agent → veille sur les sujets actifs
    └── coach_agent   → rappelle les objectifs d'apprentissage
    ↓
Résultats agrégés → réponse unifiée à l'utilisateur
```

---

## 🧠 Système d'anticipation

`predictor.py` analyse en continu les patterns d'usage pour **suggérer des actions avant qu'elles soient demandées**.

Exemples de patterns détectés :

| Pattern observé | Suggestion proactive |
|-----------------|---------------------|
| Chaque lundi matin → résumé GitHub | Envoi automatique sans déclenchement |
| Avant chaque sprint → plan de tâches | Proposition de plan la veille |
| Baisse d'activité sur un projet | "Tu n'as pas touché à X depuis 5 jours" |
| Recherche répétée sur un sujet | Création automatique d'une note Notion |

---

## 🖥️ Contrôle OS

Les actions OS sont les plus sensibles du projet.

**Règle absolue : toute action OS nécessite validation explicite**, même si `requires_validation` est désactivé ailleurs.

Actions disponibles :

| Action | Fichier | Niveau de risque |
|--------|---------|-----------------|
| Lire un fichier | `file_system.py` | Faible |
| Créer / déplacer un fichier | `file_system.py` | Moyen — validation requise |
| Supprimer un fichier | `file_system.py` | **Élevé — double confirmation** |
| Ouvrir une app | `app_launcher.py` | Faible |
| Fermer une app | `app_launcher.py` | Moyen — validation requise |
| Lire l'écran (OCR) | `screen_reader.py` | Faible |

---

## 🤖 Modèle local (Ollama)

Certaines tâches sont redirigées vers un modèle local pour :
- Données sensibles (code propriétaire, fichiers privés)
- Usage offline
- Réduction des coûts API

```python
# Décision de routage dans reasoning.py
if task.sensitivity == "high" or task.offline_required:
    return ollama_client.run(prompt)
else:
    return openai_client.run(prompt)
```

Modèles recommandés : `mistral`, `llama3`, `codellama` (via Ollama).

---

## 📡 Nouveaux endpoints API

### `POST /voice/start`

Démarre l'écoute micro (WebSocket stream).

### `POST /voice/stop`

Arrête l'écoute et retourne la transcription.

### `GET /agents/status`

```json
{
  "active_agents": [
    { "name": "dev_agent",      "status": "running", "task": "Analyse PR #42" },
    { "name": "research_agent", "status": "idle",    "task": null }
  ]
}
```

### `GET /anticipation/suggestions`

```json
[
  {
    "id": "sug_001",
    "message": "Tu n'as pas touché à TontineChain depuis 8 jours.",
    "action": "Reprendre ? Je peux résumer où tu en étais.",
    "confidence": 0.87
  }
]
```

---

## 🔐 Sécurité — Règles Phase 4

- Toute action OS est loggée de façon immuable — impossible à effacer via l'UI
- Le contrôle OS est **désactivé par défaut** — l'utilisateur l'active manuellement dans les settings
- Le modèle local ne reçoit jamais de clés API ou tokens OAuth
- Le wake word est traité localement (pas de stream audio vers le cloud)
- Double confirmation obligatoire pour suppression de fichier ou fermeture d'app

---

## 📐 Règles de développement — Phase 4

### Architecture

- Les agents spécialisés héritent tous d'une classe `BaseAgent` — interface unifiée
- `orchestrator.py` ne contient aucune logique métier — il délègue uniquement
- `predictor.py` lit la mémoire mais ne la modifie jamais directement

### Voix

- Le pipeline vocal est entièrement découplé du reste — on peut le désactiver sans impacter le chat
- La latence cible voix-à-voix : < 3 secondes

### Git

- Branches dédiées : `feat/voice`, `feat/os-control`, `feat/multi-agent`
- `feat/os-control` ne merge jamais directement sur `main` — passe obligatoirement par review
- Tests de sécurité OS obligatoires avant tout merge

---

## 🗺️ Roadmap globale

| Phase | Durée | Objectif | Statut |
|-------|-------|----------|--------|
| Phase 1 | 1 mois | Chat + mémoire + profil | ✅ |
| Phase 2 | 2–3 mois | Tools + planification + actions | ✅ |
| Phase 3 | 4–6 mois | Automatisation + dashboard | ✅ |
| **Phase 4** | **6–12 mois** | **Voix + OS + anticipation + multi-agents** | 🔴 En cours |

---

## 🔥 Vision finale atteinte

À ce stade, le Double Numérique est capable de :

- **Entendre** et **parler** naturellement
- **Agir** sur le système sans intervention manuelle
- **Anticiper** les besoins avant qu'ils soient exprimés
- **Coordonner** plusieurs agents spécialisés en parallèle
- **Apprendre** en continu des interactions

> Un véritable Jarvis réaliste — construit progressivement, bloc par bloc.

---

## 👤 Auteur

**Oktav** — Fullstack JS × IA  
Co-fondateur @ Excellence Team  
[LinkedIn](https://linkedin.com) · [GitHub](https://github.com)
