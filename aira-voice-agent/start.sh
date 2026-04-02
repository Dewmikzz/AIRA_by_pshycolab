#!/bin/bash
# ═══ FILE: start.sh ═══
# Purpose: One-click launcher for Linux/macOS
# Inputs: Standard shell environment
# Outputs: Running FastAPI server

echo "══════════════════════════════════════════════"
echo "   AIRA · Psycholab AI Voice Agent (v3.0)     "
echo "══════════════════════════════════════════════"

# 1. Check Python
if ! command -v python3 &> /dev/null
then
    echo "[!] Python 3 is not installed. Please install it first."
    exit
fi

# 2. Create Venv
if [ ! -d "venv" ]; then
    echo "[*] Creating virtual environment..."
    python3 -m venv venv
fi

# 3. Activate Venv
source venv/bin/activate

# 4. Install Deps
echo "[*] Installing dependencies (this may take a few minutes)..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

# 5. Run Setup
python setup.py

# 6. Start Server
echo "[*] Starting Aira on http://localhost:8000..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
