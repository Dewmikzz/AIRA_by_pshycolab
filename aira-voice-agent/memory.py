# ═══ FILE: memory.py ═══
# Purpose: Session history for real-time voice calls (Stateless & Stateful)
# Inputs: session_id, message (role, content)
# Outputs: Current conversation context

import logging
from typing import List, Dict
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AiraMemory")

class SessionMemory:
    def __init__(self):
        self.sessions: Dict[str, List[Dict[str, str]]] = {}
        self.last_active: Dict[str, float] = {}

    def get(self, session_id: str) -> List[Dict[str, str]]:
        """Retrieves history for a session (Stateful)."""
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        self.last_active[session_id] = time.time()
        return self.sessions[session_id]

    def add(self, session_id: str, role: str, content: str):
        """Adds a new message to the session history (Stateful)."""
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        self.sessions[session_id].append({"role": role, "content": content})
        self.last_active[session_id] = time.time()
        if len(self.sessions[session_id]) > 10:
            self.sessions[session_id] = self.sessions[session_id][-10:]

    @staticmethod
    def append_stateless(history: List[Dict[str, str]], role: str, content: str) -> List[Dict[str, str]]:
        """Stateless helper to append to history for Vercel functions."""
        new_history = list(history) if history else []
        new_history.append({"role": role, "content": content})
        return new_history[-10:] # Keep window small for token limits

    def reset(self, session_id: str):
        """Clears memory for a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            if session_id in self.last_active:
                del self.last_active[session_id]
            logger.info(f"Memory reset for session: {session_id}")

# Global singleton (Still available for local/WS usage)
memory = SessionMemory()
