@echo off
REM ═══ FILE: start.bat ═══
REM Resilient Quick-Start for Aira MVP

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

REM 4. Fix pip and Install Core
echo [*] Upgrading pip...
python -m pip install --upgrade pip --quiet

echo [*] Installing Core System (FastAPI, Uvicorn)...
echo [NOTE] Avoiding numpy/psutil to bypass path-encoding issues with '™' symbol.
python -m pip install --no-cache-dir fastapi==0.109.0 uvicorn==0.27.0 python-multipart==0.0.6 python-dotenv==1.0.0 jinja2==3.1.3 --quiet

REM 5. Attempt Heavy AI (Non-blocking)
echo [*] Attempting to install Local-AI modules...
echo [WAIT] This might show errors if your path has symbols like '™'.
echo [INFO] Aira will still start in Mock Mode if these fail.
python -m pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu --quiet
python -m pip install --no-cache-dir TTS openai-whisper==20231117 --quiet

REM 6. Start Aira
echo ══════════════════════════════════════════════
echo    Aira is starting on http://localhost:8000
echo    Mock Mode is ACTIVE by default
echo ══════════════════════════════════════════════
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause
