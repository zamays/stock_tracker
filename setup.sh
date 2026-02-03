#!/bin/bash

# Stock Tracker Setup Script
# This script is idempotent - safe to run multiple times

set -e  # Exit on error

echo "========================================"
echo "Stock Tracker Setup"
echo "========================================"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Create virtual environment if it doesn't exist
echo ""
echo "[1/6] Checking virtual environment..."
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

# 2. Activate virtual environment
echo ""
echo "[2/6] Activating virtual environment..."
source .venv/bin/activate
echo "Virtual environment activated."

# 3. Install/upgrade dependencies
echo ""
echo "[3/6] Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "Dependencies installed."

# 4. Create .env file if it doesn't exist
echo ""
echo "[4/6] Checking environment configuration..."
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    # Set SQLite as default for local development
    if grep -q "USE_SQLITE=" .env; then
        sed -i '' 's/USE_SQLITE=.*/USE_SQLITE=True/' .env 2>/dev/null || \
        sed -i 's/USE_SQLITE=.*/USE_SQLITE=True/' .env
    else
        echo "USE_SQLITE=True" >> .env
    fi
    echo ".env file created with SQLite enabled."
else
    echo ".env file already exists."
fi

# 5. Create instance directory for SQLite database
echo ""
echo "[5/6] Creating instance directory..."
mkdir -p instance
echo "Instance directory ready."

# 6. Initialize database
echo ""
echo "[6/6] Initializing database..."
python -c "
from app import create_app
from app.models import db

app = create_app()
with app.app_context():
    db.create_all()
    print('Database tables initialized.')
"

echo ""
echo "========================================"
echo "Setup complete!"
echo "========================================"
echo ""
echo "To run the application:"
echo "  source .venv/bin/activate"
echo "  python run.py"
echo ""
echo "Then open http://localhost:5001 in your browser."
echo ""
echo "Utility scripts (run from project root):"
echo "  python scripts/init_db.py           - Initialize database"
echo "  python scripts/backfill_history.py  - Backfill historical data"
echo "  python scripts/create_sample_data.py - Create sample test data"
