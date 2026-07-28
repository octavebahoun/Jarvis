# 16 — Logger les échecs LLM (au lieu de les avaler silencieusement)

## Le problème

En testant en conditions réelles (backend sur Termux/Android), une erreur LLM
survenait mais **rien n'apparaissait dans les logs du serveur** — seules des
lignes `200 OK` standard (le flux renvoie toujours un 200, voir doc 10). Le
frontend affichait bien "Le LLM a rencontré une erreur...", mais impossible de
savoir *pourquoi* (clé API manquante ? mauvais provider ? réseau ?) sans
logging côté backend.

## Ce qui a été corrigé

`agent/controller.py` : les deux points où une exception LLM est interceptée
(`handle_chat` → `AgentUnavailableError`, `stream_chat` → `STREAM_ERROR_MARKER`)
loggent maintenant la stack trace complète via `logger.exception(...)`, avec
le `chat_provider` configuré en contexte. Rien ne change côté comportement
HTTP (toujours 502 / marqueur de flux) — seule l'observabilité change : la
vraie cause apparaît désormais dans la console `uvicorn`.

## Prochaine étape pour diagnostiquer un vrai cas

Relancer l'appel qui échoue et lire la stack trace dans le terminal backend —
les causes les plus probables restent :
- `OPENAI_API_KEY` (ou `OPENROUTER_API_KEY` si `CHAT_PROVIDER=openrouter`)
  absente ou invalide dans `backend/.env`.
- `.env` pas chargé (mauvais dossier de lancement d'`uvicorn`, doit être lancé
  depuis `backend/` avec `.env` au même endroit).
- Pas de connexion sortante vers `api.openai.com` / `openrouter.ai` depuis
  l'environnement (ex. réseau mobile restrictif).

## Vérifié

Suite complète (20 tests) revérifiée après le changement.
