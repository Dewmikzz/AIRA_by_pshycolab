# ═══ FILE: agent.py ═══
# Purpose: Aira LLM brain using Ollama
# Inputs: User's transcribed text, session_id
# Outputs: Aira's text response

import ollama
import os
import logging
from typing import List, Dict
from memory import memory
from health import select_model, check_ram, check_ollama

# [THINK] Why llamas 3.2? It's the sweet spot for 4GB RAM students.
# [THINK] System prompt on every call ensures consistency, but memory keeps context.
# [THINK] Callback protocol logic must be explicit in the instructions to the LLM.

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AiraAgent")

SYSTEM_PROMPT = """
You are Aira, a senior AI receptionist for Psycholab IT company in Sri Lanka. 
Company URL: psycholab.com
Services Psycholab offers:
- Custom web development (React, Next.js, Laravel)
- Mobile app development (Flutter, React Native)
- IT infrastructure & cloud (AWS, GCP, Azure)
- Cybersecurity audits & penetration testing
- AI & automation solutions
- IT consulting & digital transformation
- 24/7 technical support contracts

YOUR PERSONA:
- Friendly, professional, concise female receptionist.
- Tone: Warm, helpful, never robotic.
- Response length: 1–2 sentences MAX. (Crucial, this is for voice output).
- Language: English primary. Handle basic Malay gracefully if needed.
- Greet users with: "Hi! Welcome to Psycholab. I'm Aira — how can I help you today?"
- Never reveal you are an AI or using open source models. Say "I'm Aira, Psycholab's assistant."

PROTOCOL:
1. If the user presents an issue or needs help:
   - Ask for their Full Name.
   - Ask for their Phone Number.
   - Ask for a one-sentence summary of the issue.
2. Once collected, say exactly: "Perfect, our team will call you within 2 hours."
"""

class AiraAgent:
    def __init__(self):
        self.model = os.getenv("OLLAMA_MODEL") or select_model(check_ram())

    def ask(self, user_text: str, session_id: str) -> str:
        """Processes user input and generates a response."""
        if not check_ollama():
            return "Hi there! Our AI is just warming up. Can you please wait a moment?"

        # Special greeting trigger
        if user_text.lower() == "greet":
            return "Hi! Welcome to Psycholab. I'm Aira — how can I help you today?"

        # Get history from memory
        history = memory.get(session_id)
        
        # Prepare messages
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_text})

        try:
            logger.info(f"Asking Ollama ({self.model}): {user_text}")
            response = ollama.chat(
                model=self.model,
                messages=messages,
                options={"temperature": 0.7, "num_predict": 80}
            )
            
            reply = response.get("message", {}).get("content", "").strip()
            
            # Clean reply (strip markdown)
            reply = reply.replace("*", "").replace("#", "").replace("`", "")
            
            # Truncate if too long (safety check)
            if len(reply) > 300:
                sentences = reply.split(".")
                reply = ". ".join(sentences[:2]) + "."

            # Store in memory
            memory.add(session_id, "user", user_text)
            memory.add(session_id, "assistant", reply)
            
            return reply

        except Exception as e:
            logger.error(f"Agent Error: {e}")
            return "I'm sorry, I'm having a little trouble connecting. Could you say that again?"

# Global singleton
agent = AiraAgent()
