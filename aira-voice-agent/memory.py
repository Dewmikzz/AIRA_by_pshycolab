# ═══ FILE: memory.py ═══
# Purpose: Manage session history with persistence
# Inputs: user_id/session_id, messages (role/content)
# Outputs: retrieval of history for LLM context

import json
import os
import time
from pathlib import Path
from typing import List, Dict, Optional
import threading

# [THINK] Why LRU? Don't want to blow up RAM if Psycholab gets 1000 hits in a day.
# [THINK] JSON backup prevents history loss if the laptop restarts.

class SessionMemory:
    def __init__(self, data_dir: str = "./data", max_sessions: int = 20):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.backup_path = self.data_dir / "sessions.json"
        self.max_sessions = max_sessions
        self.sessions: Dict[str, List[Dict[str, str]]] = {}
        self.last_access: Dict[str, float] = {}
        self._load_backup()
        
        # Periodic backup thread
        self.lock = threading.Lock()
        self.stop_backup = False
        self._start_backup_thread()

    def _load_backup(self):
        """Loads state from JSON if it exists."""
        if self.backup_path.exists():
            try:
                with open(self.backup_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.sessions = data.get("sessions", {})
                    self.last_access = {sid: time.time() for sid in self.sessions}
            except Exception as e:
                print(f"Error loading session backup: {e}")

    def _save_backup(self):
        """Saves current sessions to disk."""
        with self.lock:
            try:
                with open(self.backup_path, 'w', encoding='utf-8') as f:
                    json.dump({"sessions": self.sessions}, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"Error saving session backup: {e}")

    def _start_backup_thread(self):
        """Runs a background thread to sync to disk every 5 minutes."""
        def run():
            while not self.stop_backup:
                time.sleep(300) # 5 minutes
                self._save_backup()
        threading.Thread(target=run, daemon=True).start()

    def add(self, session_id: str, role: str, content: str):
        """Adds a message to a session and handles LRU eviction."""
        with self.lock:
            if session_id not in self.sessions:
                if len(self.sessions) >= self.max_sessions:
                    # Evict oldest
                    oldest = min(self.last_access, key=self.last_access.get)
                    del self.sessions[oldest]
                    del self.last_access[oldest]
                self.sessions[session_id] = []
            
            self.sessions[session_id].append({"role": role, "content": content})
            self.last_access[session_id] = time.time()
            
            # Keep history short (last 8 messages = 4 turns)
            if len(self.sessions[session_id]) > 8:
                self.sessions[session_id] = self.sessions[session_id][-8:]

    def get(self, session_id: str) -> List[Dict[str, str]]:
        """Retrieves session history."""
        self.last_access[session_id] = time.time()
        return self.sessions.get(session_id, [])

    def reset(self, session_id: str):
        """Clears a specific session."""
        with self.lock:
            if session_id in self.sessions:
                self.sessions[session_id] = []
                self.last_access[session_id] = time.time()

# Global singleton
memory = SessionMemory(data_dir=os.getenv("DATA_DIR", "./data"))
