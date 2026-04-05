@echo off
REM ═══ FILE: start.bat ═══
REM Production-Grade One-Click Launcher for Aira

echo ══════════════════════════════════════════════
echo    AIRA · Production Voice Call (v4.0)     
echo ══════════════════════════════════════════════

REM 1. Check for API Keys
if not exist .env (
    echo [!] .env file not found. Creating from example...
    copy .env.example .env
    echo [!] PLEASE EDIT .env AND ADD YOUR GROQ_API_KEY AND OPENROUTER_API_KEY.
    pause
    exit /b
)

REM 2. Create Venv
if not exist venv (
    echo [*] Creating virtual environment...
    python -m venv venv
)

REM 3. Activate Venv
call venv\Scripts\activate

REM 4. Install Dependencies
echo [*] Installing production dependencies...
pip install -r requirements.txt --quiet

REM 5. Start Server
echo ══════════════════════════════════════════════
echo    Aira is starting on http://localhost:8000
echo    Ensure you have internet for Cloud APIs!
echo ══════════════════════════════════════════════
python main.py

pause
