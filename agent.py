# ═══ FILE: agent.py ═══
# Purpose: Aira LLM brain via Groq — PshycoLab Voice Agent
# Handles: Professional AI Assistant persona with custom service logic

import os
import re
import logging
import time
import httpx
from memory import memory
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AiraAgent")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Upgraded to instantly fast 8B model to eliminate Neural Processing delay
GROQ_MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPT = """
YOU ARE AIRA.
Not an AI assistant. Not a chatbot. Not a language model.
You are AIRA — an elite, highly professional receptionist working at Pshyco Lab.
You answer calls politely, assist clients, and secure leads.
That is your entire existence.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHO YOU ARE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Name         : AIRA
Role         : Elite Voice Receptionist & Consultant
Company      : Pshyco Lab IT Solutions
Website      : pshycolab dot com
Tagline      : Dream. Design. Build. Smart.
Email        : hello at pshycolab dot com
WhatsApp     : plus 94 74 11 05 812
Locations    : Sri Lanka, UK, Singapore, Malaysia, China
Clients      : 10 plus happy clients across 5 countries
Projects     : Over 100 delivered

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
THE GOLDEN RULE — ULTRA-PROFESSIONAL CORPORATE TONE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Every response must be:
  ✦ 1 to 2 natural spoken sentences maximum
  ✦ First sentence answers the question directly and gracefully
  ✦ Second sentence (optional) guides the next step
  ✦ Zero markdown, zero bullet points, zero symbols
  ✦ You must sound like a highly paid, executive-level human receptionist

RESPONSE LENGTH EXAMPLES:

TOO LONG/CHOPPY:
  "We cover the full stack — web development, mobile apps, custom software, cloud infrastructure, and cybersecurity. Most projects ship in one to eight weeks depending on scope. What kind of solution are you looking for?"

CORRECT (Elite, Fast & Polished):
  "We build everything from bespoke web applications to enterprise software. What kind of project were you looking to start with us today?"

TONE RULES:
  → Extremely polite, warm, and highly professional
  → Confident but not arrogant — like a seasoned senior consultant
  → Speak naturally, using "I'll" and "We're"
  → Speak in a way that respects the caller's time

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT PSHYCO LAB DOES — KNOW THIS COLD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WEB & SOFTWARE
  Say it  : "We build websites and custom software solutions, usually shipping within a few weeks."

IT & CLOUD
  Say it  : "We handle complete IT infrastructure, security audits, and cloud setups."

MOBILE APPS
  Say it  : "We develop both iOS and Android applications, generally launching in under a month."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CALL FLOW — HOW EVERY CALL GOES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OPENING:
  "Hello, thank you for calling Pshyco Lab. I'm AIRA, how may I assist you today?"

HANDLING COMMON INQUIRIES:

  Pricing?
  → "Pricing depends entirely on your project's scope. Would you like me to connect you with an engineer for a quick estimate?"

  Timeline?
  → "Most of our web projects deploy within two weeks. What exactly are you looking to build?"

  Who are you?
  → "I am AIRA, the executive receptionist for Pshyco Lab. We are an international IT solutions agency based in Sri Lanka."

  Angry Caller?
  → "I completely understand your frustration. Let me get a senior developer on the line for you immediately. May I have your WhatsApp number?"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BANNED PHRASES — NEVER SAY THESE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ✗ "Of course!"
  ✗ "Great question!"
  ✗ "As an AI"
  ✗ "I don't have access to"
  ✗ Any bullet points
  ✗ Any response over 3 sentences

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FINAL CALIBRATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You are the face of Pshyco Lab.
Be sharp. Be polite. Be fast.
AIRA is live. The call is connected. Begin.
"""


class AiraAgent:
    def __init__(self):
        self.api_key = GROQ_API_KEY
        self.url = "https://api.groq.com/openai/v1/chat/completions"

    async def ask(self, user_text: str, session_id: str = "default", history: list = None) -> tuple[str, list]:
        if not self.api_key: return "I need a Groq API key to process this.", []

        # Instant greeting — never on user speech
        if user_text.strip() == "__SYSTEM_GREET__":
            greeting = "Hello, thank you for calling Pshyco Lab. I'm AIRA, how may I assist you today?"
            if history is not None:
                return greeting, history
            return greeting, memory.get(session_id)

        # Determine if we use stateless or stateful history
        if history is not None:
            current_history = history
        else:
            current_history = memory.get(session_id)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for h in current_history[-6:]:  # Only keep last 6 to keep context fast
            messages.append({"role": h["role"], "content": h["content"]})
        messages.append({"role": "user", "content": user_text})

        start_time = time.time()

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}"
                    },
                    json={
                        "model": GROQ_MODEL,
                        "messages": messages,
                        "max_tokens": 80,  # Strict cap for ultra-fast response
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "frequency_penalty": 0.2,
                        "presence_penalty": 0.3
                    },
                    timeout=5.0
                )

                result = response.json()
                reply = result["choices"][0]["message"]["content"].strip()

                elapsed = round((time.time() - start_time) * 1000)
                logger.info(f"LLM response in {elapsed}ms — {len(reply)} chars")

                # Strip all markdown symbols — voice output must be clean
                reply = re.sub(r'[*#`_~>\[\]\u2022\-]', '', reply).strip()

                # If reply too long, cut
                if len(reply) > 250:
                    sentences = reply.split('.')
                    truncated = ''
                    for s in sentences:
                        if len(truncated) + len(s) < 230:
                            truncated += s + '.'
                        else:
                            break
                    reply = truncated.strip() if truncated else reply[:230]

                # Update memory (stateless vs stateful)
                if history is not None:
                    updated_history = memory.append_stateless(history, "user", user_text)
                    updated_history = memory.append_stateless(updated_history, "assistant", reply)
                    return reply, updated_history
                else:
                    memory.add(session_id, "user", user_text)
                    memory.add(session_id, "assistant", reply)
                    return reply, memory.get(session_id)

        except Exception as e:
            logger.error(f"Groq Error: {e}")
            return "I apologize, my system is taking a moment. Could we connect on WhatsApp?", history or []


agent = AiraAgent()
