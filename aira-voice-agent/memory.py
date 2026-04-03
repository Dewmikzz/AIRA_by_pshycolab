# ═══ FILE: memory.py ═══
# Purpose: In-memory session history for real-time voice calls
# Inputs: session_id, message (role, content)
# Outputs: Current conversation context

import logging
from typing import List, Dict
import time

# [THINK] Why not a DB? For a production MVP, in-memory is the fastest way to handle 
# sub-second response times. We can add Redis/PostgreSQL in v2.

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AiraMemory")

class SessionMemory:
    def __init__(self):
        self.sessions: Dict[str, List[Dict[str, str]]] = {}
        self.last_active: Dict[str, float] = {}

    def get(self, session_id: str) -> List[Dict[str, str]]:
        """Retrieves history for a session. If not found, initializes it."""
        if session_id not in self.sessions:
            self.sessions[session_id] = []
            
        self.last_active[session_id] = time.time()
        return self.sessions[session_id]

    def add(self, session_id: str, role: str, content: str):
        """Adds a new message to the session history."""
        if session_id not in self.sessions:
            self.sessions[session_id] = []
            
        self.sessions[session_id].append({"role": role, "content": content})
        self.last_active[session_id] = time.time()
        
        # Cleanup logic (optional): Keep only latest 10 messages for speed
        if len(self.sessions[session_id]) > 10:
            self.sessions[session_id] = self.sessions[session_id][-10:]

    def reset(self, session_id: str):
        """Clears memory for a session (useful for End Call)."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            del self.last_active[session_id]
            logger.info(f"Memory reset for session: {session_id}")

# Global singleton
memory = SessionMemory()
