#!/bin/bash
# SmartFarm OS — Quick Setup Script

set -e

echo "🌿 SmartFarm OS Setup"
echo "====================="

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "❌ Python 3.10+ required. Install from python.org"
    exit 1
fi

PYVER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Python $PYVER detected"

# Create venv
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

# Install deps
echo "📦 Installing dependencies..."
pip install -r requirements.txt -q

# Copy env
if [ ! -f ".env" ]; then
    cp config/.env.example .env
    echo "📝 Created .env from template. Edit with your settings."
fi

# Seed DB
echo "🌱 Initializing database..."
python -m backend.seeds.seed_data

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the server:"
echo "  source venv/bin/activate"
echo "  uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "API Docs: http://localhost:8000/docs"
echo "Login: admin / admin123"
