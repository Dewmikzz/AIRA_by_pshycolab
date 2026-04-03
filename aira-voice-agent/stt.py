# ═══ FILE: stt.py ═══
# Purpose: Real-time Cloud Speech-to-Text via Groq Whisper API
# Inputs: Audio bytes (Raw PCM)
# Outputs: Transcribed text string

import os
import httpx
import logging
import tempfile
import time
import struct
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AiraSTT")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/audio/transcriptions"

def get_wav_header(pcm_length: int, sample_rate: int = 16000, num_channels: int = 1, bit_depth: int = 16) -> bytes:
    """Manually constructs a 44-byte WAV header for raw PCM data."""
    header = bytearray(44)
    # RIFF header
    header[0:4] = b'RIFF'
    struct.pack_into('<I', header, 4, 36 + pcm_length)
    header[8:12] = b'WAVE'
    # fmt chunk
    header[12:16] = b'fmt '
    struct.pack_into('<I', header, 16, 16) # fmt chunk size
    struct.pack_into('<H', header, 20, 1)  # Audio format (1 = PCM)
    struct.pack_into('<H', header, 22, num_channels)
    struct.pack_into('<I', header, 24, sample_rate)
    struct.pack_into('<I', header, 28, sample_rate * num_channels * (bit_depth // 8)) # Byte rate
    struct.pack_into('<H', header, 32, num_channels * (bit_depth // 8)) # Block align
    struct.pack_into('<H', header, 34, bit_depth)
    # data chunk
    header[36:40] = b'data'
    struct.pack_into('<I', header, 40, pcm_length)
    return bytes(header)

class GroqSTT:
    def __init__(self):
        self.api_key = GROQ_API_KEY

    async def transcribe(self, audio_bytes: bytes, filename: str = "speech.wav") -> str:
        """Sends audio bytes to Groq for whisper-large-v3 transcription."""
        if not self.api_key:
            logger.error("GROQ_API_KEY is missing!")
            return "__error__"

        if not audio_bytes or len(audio_bytes) < 3000: # Threshold for meaningful speech
            return "__silence__"

        start_time = time.time()
        
        # [THINK] Raw PCM bytes need a WAV header to be a valid file for Groq.
        # We manually prepend the header to bypass Python 3.13/pydub issues.
        wav_header = get_wav_header(len(audio_bytes))
        full_wav_data = wav_header + audio_bytes

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(full_wav_data)
            tmp_path = tmp.name

        try:
            async with httpx.AsyncClient() as client:
                with open(tmp_path, "rb") as f:
                    files = {"file": (filename, f, "audio/wav")}
                    data = {
                        "model": "whisper-large-v3",
                        "response_format": "json"
                        # [Sri Lanka Fix] Removing fixed "en" language to allow auto-detection of Sinhala/English
                    }
                    headers = {"Authorization": f"Bearer {self.api_key}"}
                    
                    response = await client.post(
                        GROQ_ENDPOINT,
                        headers=headers,
                        files=files,
                        data=data,
                        timeout=10.0
                    )
                
                if response.status_code != 200:
                    logger.error(f"Groq API Error: {response.text}")
                    return "__error__"
                
                result = response.json()
                text = result.get("text", "").strip()
                
                logger.info(f"Groq STT ({time.time() - start_time:.2f}s): {text}")
                
                if len(text) < 2:
                    return "__silence__"
                return text

        except Exception as e:
            logger.error(f"STT Exception: {e}")
            return "__error__"
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

# Global singleton
stt = GroqSTT()
