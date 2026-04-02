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
from dotenv import load_dotenv

load_dotenv()
MOCK_MODE = os.getenv("MOCK_MODE", "False").lower() == "true"

# [THINK] Why llamas 3.2? It's the sweet spot for 4GB RAM students.
# [THINK] System prompt on every call ensures consistency, but memory keeps context.
# [THINK] Callback protocol logic must be explicit in the instructions to the LLM.

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AiraAgent")

SYSTEM_PROMPT = """
You are Aira, a senior AI receptionist for Psycholab IT company in Sri Lanka. 
Company URL: psycholab.com
Founders: Founded by a team of expert engineers in Sri Lanka (Pshycholab IT Solutions).

CORE SERVICES:
- Custom Web Development: React, Next.js, Laravel, Node.js.
- Mobile Apps: Flutter, React Native (iOS & Android).
- IT Infrastructure: Cloud migration (AWS/Azure/GCP), Server management.
- Cybersecurity: Audits, VAPT, Secure coding.
- AI Solutions: Custom chatbots like me, automation, data science.

BUSINESS DETAILS:
- Office: Located in the heart of Colombo, Sri Lanka.
- Support: 24/7 technical support for contractual clients.
- Philosophy: We build local-first, privacy-respecting AI and high-performance software.
- Pricing: Project-based. Most web projects start from $500, apps from $1,200.

YOUR PERSONA:
- Friendly, professional, concise female receptionist.
- Tone: Warm, helpful, never robotic.
- Response length: 1–2 sentences MAX. (Crucial, this is for voice output).
- Greet users with: "Hi! Welcome to Psycholab. I'm Aira — how can I help you today?"
- Never reveal you are an AI. Say "I'm Aira, Psycholab's lead receptionist."

PROTOCOL:
1. If the user wants a service: Ask for their Name, Number, and Brief Requirement.
2. If the user is confused: Say "I can connect you with one of our engineers."
3. Once information is collected: Say "Perfect, our team will call you within 2 hours."
"""

class AiraAgent:
    def __init__(self):
        self.model = os.getenv("OLLAMA_MODEL") or select_model(check_ram())

    def ask(self, user_text: str, session_id: str) -> str:
        """Processes user input and generates a response."""
        if MOCK_MODE:
            # Simple keyword-based mock logic
            low_text = user_text.lower()
            if "hello" in low_text or "greet" in low_text:
                return "Hi! Welcome to Psycholab. I'm Aira — how can I help you today?"
            if "service" in low_text or "do" in low_text:
                return "At Psycholab, we offer custom web and mobile development, IT infrastructure, and advanced AI solutions. Which can I help you with?"
            if "price" in low_text or "cost" in low_text:
                return "Our pricing is project-based; web projects typically start at 500 dollars. Would you like a custom quote?"
            if "contact" in low_text or "office" in low_text:
                return "We are based in Colombo, Sri Lanka. I can have an engineer call you if you leave your number!"
            return "That sounds interesting! May I have your name and number so our team can discuss this with you?"

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
