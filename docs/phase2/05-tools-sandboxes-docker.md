# 05 — Tools sandboxés (code_executor, browser_automation/Playwright)

## Ce qui a été construit

- `tools/_sandbox.py` : mécanique Docker partagée (`run_in_container`), pas
  un tool en soi — utilisée par les deux tools sensibles pour éviter de
  dupliquer le cycle de vie du container. Crée un container jetable, le
  démarre, attend avec un **timeout strict** (tue et lève
  `SandboxTimeoutError` si dépassé), et le **supprime systématiquement**
  (`finally`, y compris en cas d'erreur ou de timeout).
- `tools/code_executor.py` : exécute du code Python fourni par le LLM dans un
  container jetable **réseau désactivé** (`network_disabled=True`), mémoire
  et CPU plafonnés. `requires_validation = True`.
- `tools/browser_automation.py` : Playwright, container basé sur l'image
  officielle `mcr.microsoft.com/playwright/python`, **réseau activé**
  (`network_disabled=False`) — contrairement à `code_executor`, il doit
  pouvoir atteindre de vrais sites. `requires_validation = True`.
- Résultats des deux tools tronqués à 10 000 caractères (`MAX_OUTPUT_CHARS`,
  règle explicite de `phase2.md`).
- `docker-compose.yml` : le service `backend` monte
  `/var/run/docker.sock` — nécessaire pour que le backend puisse lancer des
  containers "frères" (docker-out-of-docker, pas de Docker-in-Docker imbriqué).

## Décision : SDK Docker Python (choisi avec l'utilisateur)

Plutôt que `subprocess` + CLI `docker run` — plus robuste (pas de parsing de
sortie shell), plus facile à tester (le client peut être entièrement simulé).

## Ce qui n'a pas pu être vérifié ici

Aucun daemon Docker n'est disponible dans ce sandbox : les tests simulent
entièrement le client Docker (`docker.from_env()` remplacé par un faux client
dont les containers sont de simples objets Python). Ils vérifient la
mécanique (démarrage, timeout → kill, suppression garantie, réseau
activé/désactivé selon le tool) mais **pas** qu'un vrai container Docker
s'exécute correctement, ni que l'image Playwright (`v1.49.0-noble`, la
version peut être à ajuster) est valide — à vérifier sur ta machine avec
Docker actif une fois les tools atteignables depuis l'API (bloc suivant).

Ces deux tools sont câblés dans le registre mais pas encore atteignables
depuis l'API — la vérification bout-en-bout viendra avec les blocs API +
frontend.

## Vérifié (dans ce tour)

15 tests (`test_sandbox.py`, `test_code_executor.py`,
`test_browser_automation.py`) : cycle de vie du container (démarrage,
suppression garantie, timeout → kill), séparation réseau
désactivé/activé selon le tool, troncature des résultats, arguments transmis
correctement (URL, sélecteur CSS). Suite complète : 54 tests.
