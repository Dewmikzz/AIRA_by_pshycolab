# ═══ FILE: tts.py ═══
# Purpose: Professional Cloud Text-to-Speech via Premium Neural Voices
# Inputs: Text string
# Outputs: Audio bytes (High-Fidelity MP3)

import os
import logging
import httpx
import re
import edge_tts
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AiraTTS")

CARTESIA_API_KEY = os.getenv("CARTESIA_API_KEY")

# Best natural male voice on Cartesia — "Clony"
CARTESIA_VOICE_ID = "79a125e8-cd45-4c13-8a67-188112f4dd22"


class PremiumNeuralTTS:

    def clean(self, text: str) -> str:
        """Strip markdown symbols that sound bad in TTS."""
        text = re.sub(r'[*#`_~>\[\]•]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    async def synthesize(self, text: str) -> bytes:
        """Synthesizes text using Cartesia (Primary) with Edge-TTS fallback."""
        text = self.clean(text)
        if not text:
            return b""

        # PRIMARY: Cartesia via httpx (no SDK — direct REST call)
        if CARTESIA_API_KEY:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    resp = await client.post(
                        "https://api.cartesia.ai/tts/bytes",
                        headers={
                            "X-API-Key": CARTESIA_API_KEY,
                            "Cartesia-Version": "2024-06-10",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model_id": "sonic-english",
                            "transcript": text,
                            "voice": {
                                "mode": "id",
                                "id": CARTESIA_VOICE_ID
                            },
                            "output_format": {
                                "container": "mp3",
                                "bit_rate": 128000,
                                "sample_rate": 44100
                            }
                        }
                    )
                    if resp.status_code == 200 and len(resp.content) > 100:
                        logger.info(f"Cartesia OK — {len(resp.content)} bytes")
                        return resp.content
                    else:
                        logger.error(f"Cartesia {resp.status_code}: {resp.text[:200]}")
            except Exception as e:
                logger.error(f"Cartesia failed: {e}")

        # FALLBACK: Edge-TTS male voice
        logger.info("Falling back to Edge-TTS male voice (GuyNeural)")
        try:
            communicate = edge_tts.Communicate(text, "en-US-GuyNeural")
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            if len(audio_data) > 100:
                return audio_data
        except Exception as e:
            logger.error(f"Edge-TTS failed: {e}")

        return b""


# Global singleton
tts = PremiumNeuralTTS()
