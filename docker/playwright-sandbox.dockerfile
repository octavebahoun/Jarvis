# Image du sandbox utilisé par le tool browser_automation.
#
# L'image officielle mcr.microsoft.com/playwright/python fournit les
# navigateurs (Chromium/Firefox/WebKit) et leurs dépendances système, mais PAS
# le paquet pip "playwright" lui-même — cf.
# docs/phase2/15-fix-image-playwright-sans-paquet-pip.md. Sans lui, le script
# exécuté dans le container plante avec `ModuleNotFoundError: No module named
# 'playwright'`.
#
# Version du paquet pip alignée sur le tag de l'image (v1.49.0) : Playwright
# est strict sur la correspondance exacte entre le paquet et la version des
# navigateurs embarqués.
FROM mcr.microsoft.com/playwright/python:v1.49.0-noble

RUN pip install --no-cache-dir playwright==1.49.0
