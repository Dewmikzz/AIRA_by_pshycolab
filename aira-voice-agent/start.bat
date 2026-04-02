@echo off
REM ═══ FILE: start.bat ═══
REM Purpose: One-click launcher with resilient installation for Aira
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

REM 4. Resilient Installation
echo [*] Installing Core System (FastAPI, Uvicorn)...
pip install -r requirements-core.txt --quiet
if %errorlevel% neq 0 (
    echo [!] Core installation failed. Checking internet connection...
    pause
    exit /b
)

echo [*] Attempting to install Local-AI modules (Torch, TTS, Whisper)...
echo [NOTE] If this part fails, Aira will still run in 'Mock Mode'.
pip install torch --index-url https://download.pytorch.org/whl/cpu --quiet
pip install TTS --quiet
pip install openai-whisper==20231117 --quiet
pip install -r requirements.txt --quiet

REM 5. Run Setup (Checks Ollama/FFmpeg)
echo [*] Running system health check...
python setup.py

REM 6. Start Server
echo ══════════════════════════════════════════════
echo    Aira is starting on http://localhost:8000
echo    Mock Mode is ACTIVE by default
echo ══════════════════════════════════════════════
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause
