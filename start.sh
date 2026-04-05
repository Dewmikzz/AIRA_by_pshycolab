#!/bin/bash
# ═══ FILE: start.sh ═══
# Production-Grade One-Click Launcher for Aira

echo "══════════════════════════════════════════════"
echo "   AIRA · Production Voice Call (v4.0)        "
echo "══════════════════════════════════════════════"

# 1. Check for API Keys
if [ ! -f .env ]; then
    echo "[!] .env file not found. Creating from example..."
    cp .env.example .env
    echo "[!] PLEASE EDIT .env AND ADD YOUR GROQ_API_KEY AND OPENROUTER_API_KEY."
    exit 1
fi

# 2. Create Venv
if [ ! -d "venv" ]; then
    echo "[*] Creating virtual environment..."
    python3 -m venv venv
fi

# 3. Activate Venv
source venv/bin/activate

# 4. Install Dependencies
echo "[*] Installing production dependencies..."
pip install -r requirements.txt --quiet

# 5. Start Server
echo "══════════════════════════════════════════════"
echo "   Aira is starting on http://localhost:8000"
echo "   Ensure you have internet for Cloud APIs!"
echo "══════════════════════════════════════════════"
python3 main.py
