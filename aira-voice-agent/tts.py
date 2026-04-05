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
from cartesia import Cartesia
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AiraTTS")

# --- [CONFIG] ---
CARTESIA_API_KEY = os.getenv("CARTESIA_API_KEY")
CARTESIA_VOICE_ID = os.getenv("CARTESIA_VOICE_ID", "9626c31c-bec5-4cca-baa8-f8ba9e84c8bc")
DEFAULT_VOICE = os.getenv("TTS_VOICE", "en-US-AvaNeural") # Fallback voice for Edge-TTS

class PremiumNeuralTTS:
    def __init__(self):
        self.cartesia_client = None
        if CARTESIA_API_KEY:
            try:
                self.cartesia_client = Cartesia(api_key=CARTESIA_API_KEY)
                logger.info("Cartesia engine initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Cartesia: {e}")
        else:
            logger.warning("CARTESIA_API_KEY not found. Falling back to Edge-TTS.")

    async def synthesize(self, text: str) -> bytes:
        """Synthesizes text using Cartesia (Primary) with cascading fallbacks."""
        if not text:
            return b""

        # 1. Primary Engine: Cartesia (Premium)
        if self.cartesia_client:
            try:
                logger.info(f"Synthesizing via Cartesia | Voice: {CARTESIA_VOICE_ID}")
                # Use to_thread for the synchronous SDK call if not using async client
                # Actually Cartesia SDK has tts.generate which returns a generator or bytes
                # For simplicity in this request-response model, we'll use the Bytes endpoint logic
                
                # Use the 'bytes' method for non-streaming audio generation
                audio_data = await asyncio.to_thread(
                    self.cartesia_client.tts.bytes,
                    model_id="sonic-3",
                    transcript=text,
                    voice_id=CARTESIA_VOICE_ID,
                    output_format={"container": "mp3", "encoding": "mp3", "sample_rate": 44100}
                )
                
                if audio_data:
                    return audio_data
                
            except Exception as e:
                logger.error(f"Cartesia Synthesis Failed: {e}")

        # 2. Secondary Engine: Edge-TTS (High Quality Fallback)
        logger.info(f"Falling back to Edge-TTS | Voice: {DEFAULT_VOICE}")
        try:
            communicate = edge_tts.Communicate(text, DEFAULT_VOICE)
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            
            if len(audio_data) > 100:
                return audio_data
        except Exception as e:
            logger.error(f"Edge-TTS Fallback Failed: {e}")

        # 3. Final Engine: gTTS (Stability Fallback)
        logger.info("Moving to gTTS (Final Stability Fallback)...")
        try:
            return await asyncio.to_thread(self._gtts_fallback, text)
        except Exception as ge:
            logger.error(f"Critical TTS Failure: {ge}")
            return b""

    def _gtts_fallback(self, text: str) -> bytes:
        """Synchronous gTTS wrapper for thread safety."""
        # Strictly English as requested
        tts_obj = gTTS(text=text, lang="en", slow=False)
        fp = io.BytesIO()
        tts_obj.write_to_fp(fp)
        return fp.getvalue()

# Global singleton
tts = PremiumNeuralTTS()
