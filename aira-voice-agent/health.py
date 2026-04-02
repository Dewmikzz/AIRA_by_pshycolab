# ═══ FILE: health.py ═══
# Purpose: System health monitoring and model selection logic
# Inputs: System hardware stats (via psutil), service availability
# Outputs: Model names and system status JSON

import psutil
import socket
import logging
import os
from typing import Dict, Any

# [THINK] Why check RAM every time? Models change performance based on available overhead.
# [THINK] If Ollama is down, don't crash main.py, return a 'ready=False' flag so frontend can show warm-up UI.

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AiraHealth")

def check_ram() -> float:
    """Returns the total RAM in GB."""
    mem = psutil.virtual_memory()
    return mem.total / (1024 ** 3)

def select_model(available_ram_gb: float) -> str:
    """Selects the best Ollama model base on available RAM."""
    if available_ram_gb >= 16:
        return "llama3.1"  # 8B model
    elif available_ram_gb >= 8:
        return "mistral"    # 7B model
    elif available_ram_gb >= 4:
        return "llama3.2"   # 3B model (Safe choice)
    else:
        return "tinyllama"  # Emergency fallback

def check_ollama(host: str = "127.0.0.1", port: int = 11434) -> bool:
    """Checks if Ollama service is reachable."""
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False

def get_status() -> Dict[str, Any]:
    """Aggregates all health signals into a single status object."""
    ram = check_ram()
    model = os.getenv("OLLAMA_MODEL") or select_model(ram)
    
    return {
        "ram_gb": round(ram, 2),
        "ollama_online": check_ollama(),
        "recommended_model": model,
        "ready": check_ollama() # Simplification for MVP
    }

if __name__ == "__main__":
    print(f"Health Status: {get_status()}")
