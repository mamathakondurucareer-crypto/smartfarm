#!/bin/bash
# SmartFarm OS — Development Server
set -e
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
echo "🌿 Starting SmartFarm OS Development Server..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
