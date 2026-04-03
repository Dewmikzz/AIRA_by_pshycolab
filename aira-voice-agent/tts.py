# ═══ FILE: tts.py ═══
# Purpose: Professional Cloud Text-to-Speech via Premium Neural Voices
# Inputs: Text string
# Outputs: Audio bytes (High-Fidelity MP3)

import os
import logging
import asyncio
import edge_tts
import io
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AiraTTS")

# Professional Neural Voices for modern fluency
# en-US-AvaNeural is human-like and modern
DEFAULT_VOICE = os.getenv("TTS_VOICE", "en-US-AvaNeural")
SINHALA_VOICE = "si-LK-SameeraNeural" # Fluent Sri Lankan Male (if available) or si-LK-ThiliniNeural (Female)

class PremiumNeuralTTS:
    def __init__(self):
        self.voice = DEFAULT_VOICE

    async def synthesize(self, text: str) -> bytes:
        """Synthesizes text to high-fidelity audio using modern neural voices."""
        if not text:
            return b""
            
        # [THINK] For a 'Modern & Fluent' experience, we use edge-tts (Neural).
        # We fall back to gTTS (Google) only if the premium engine is blocked.
        
        # Select voice based on language
        current_voice = self.voice
        if any("\u0d80" <= char <= "\u0dff" for char in text):
            current_voice = "si-LK-ThiliniNeural" # Switch to Sri Lankan Female voice
            logger.info(f"Sinhala detected, switching to Premium Sri Lankan Voice: {current_voice}")

        try:
            communicate = edge_tts.Communicate(text, current_voice)
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            
            if len(audio_data) > 100:
                logger.info(f"Premium Neural TTS generated {len(audio_data)} bytes")
                return audio_data
            else:
                raise ValueError("Generated audio is too small")

        except Exception as e:
            logger.error(f"Premium TTS Error: {e}")
            logger.info("Falling back to gTTS for reliability...")
            try:
                # [RELIABILITY] gTTS is always the bulletproof fallback
                lang = "si" if any("\u0d80" <= char <= "\u0dff" for char in text) else "en"
                tts = gTTS(text=text, lang=lang, slow=False)
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                return fp.getvalue()
            except Exception as ge:
                logger.error(f"Fallback TTS failed: {ge}")
                return b""

# Global singleton
tts = PremiumNeuralTTS()
