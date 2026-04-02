@echo off
REM ═══ FILE: start.bat ═══
REM Purpose: One-click launcher for Windows
REM Inputs: CMD environment
REM Outputs: Running FastAPI server

echo ══════════════════════════════════════════════
echo    AIRA · Psycholab AI Voice Agent (v3.0)     
echo ══════════════════════════════════════════════

REM 1. Check Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] Python is not installed. Please install it from python.org.
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

REM 4. Specialized Install for Windows (User Request)
echo [*] Installing Torch (CPU version) first...
pip install torch --index-url https://download.pytorch.org/whl/cpu --quiet

echo [*] Installing Coqui TTS...
pip install TTS --quiet

echo [*] Installing remaining dependencies...
pip install -r requirements.txt --quiet

REM 5. Run Setup
python setup.py

REM 6. Start Server
echo [*] Starting Aira on http://localhost:8000...
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause
