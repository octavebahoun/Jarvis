#!/bin/bash

mkdir -p backend/api/routes
mkdir -p backend/agent
mkdir -p backend/memory
mkdir -p backend/identity
mkdir -p backend/db
mkdir -p frontend/app
mkdir -p frontend/components
mkdir -p frontend/lib

# Backend
touch backend/main.py
touch backend/config.py
touch backend/api/routes/chat.py
touch backend/api/routes/memory.py
touch backend/api/routes/profile.py
touch backend/api/deps.py
touch backend/agent/controller.py
touch backend/agent/reasoning.py
touch backend/memory/short_term.py
touch backend/memory/long_term.py
touch backend/memory/vector_store.py
touch backend/identity/profile.py
touch backend/db/models.py
touch backend/db/session.py

# Frontend
touch frontend/app/page.tsx
touch frontend/components/ChatWindow.tsx
touch frontend/components/InputBar.tsx
touch frontend/lib/api.ts

# Racine
touch docker-compose.yml
touch .env.example
touch README.md

echo "✅ Arborescence Phase 1 créée."
