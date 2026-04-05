# ═══ FILE: setup.py ═══
# Purpose: Environment setup and model downloader
# Inputs: System RAM, Internet connection
# Outputs: Downloaded models and verification report

import os
import subprocess
import sys
import logging
from health import check_ram, select_model, check_ollama

# [THINK] Why pull models here? uvicorn timeout is short; big model pulls will crash the app on first run.
# [THINK] Checking ffmpeg is crucial because pydub/whisper fail silently or with cryptic errors without it.

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AiraSetup")

def run_command(command: str):
    """Executes a shell command and logs output."""
    try:
        logger.info(f"Running: {command}")
        subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e}")
        return False

def check_ffmpeg():
    """Verifies ffmpeg is installed."""
    try:
        subprocess.run("ffmpeg -version", shell=True, check=True, capture_output=True)
        return True
    except:
        return False

def main():
    print("═══ AIRA SYSTEM SETUP ═══")
    
    # 1. RAM & Model detection
    ram = check_ram()
    model = os.getenv("OLLAMA_MODEL") or select_model(ram)
    print(f"[*] Detected RAM: {ram:.2f} GB")
    print(f"[*] Recommended LLM: {model}")

    # 2. Ollama check & Pull
    if check_ollama():
        print(f"[*] Pulling Ollama model: {model}...")
        run_command(f"ollama pull {model}")
    else:
        print("[!] Ollama service not detected. Please start Ollama and run 'ollama pull " + model + "' manually.")

    # 3. Whisper check
    whisper_model = os.getenv("WHISPER_MODEL", "base")
    print(f"[*] Whisper model '{whisper_model}' will be downloaded on first run via main.py.")

    # 4. ffmpeg check
    if check_ffmpeg():
        print("[✅] ffmpeg detected.")
    else:
        print("[❌] ffmpeg NOT detected. Please install ffmpeg for audio processing.")
        if sys.platform == "win32":
            print("    -> Hint: 'choco install ffmpeg' or download from ffmpeg.org")
        else:
            print("    -> Hint: 'sudo apt install ffmpeg' or 'brew install ffmpeg'")

    print("\n[✅] Setup complete. You can now run the agent.")

if __name__ == "__main__":
    main()
