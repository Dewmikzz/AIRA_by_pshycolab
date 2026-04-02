# ═══ FILE: tts.py ═══
# Purpose: Text-to-Speech using Coqui TTS with pyttsx3 fallback
# Inputs: Text string
# Outputs: Audio bytes (WAV)

import os
import tempfile
import time
import logging
import re
from pathlib import Path

# [THINK] Coqui is high quality but heavy. pyttsx3 is instant but robotic.
# [THINK] Clean text is vital: '---' or '*' in text makes TTS sound glitchy.
# [THINK] If both fail, return empty bytes so main.py knows to skip audio.

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AiraTTS")

try:
    from TTS.api import TTS
    COQUI_AVAILABLE = True
except ImportError:
    COQUI_AVAILABLE = False
    logger.warning("Coqui TTS not installed. Falling back to pyttsx3.")

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    logger.warning("pyttsx3 not installed.")

class TextToSpeech:
    def __init__(self):
        self.coqui_model_name = os.getenv("TTS_MODEL", "tts_models/en/ljspeech/vits")
        self.engine_preference = os.getenv("TTS_ENGINE", "coqui")
        self.tts_instance = None
        self.pyttsx3_engine = None

    def _load_coqui(self):
        if COQUI_AVAILABLE and self.tts_instance is None:
            try:
                logger.info(f"Loading Coqui TTS: {self.coqui_model_name}...")
                self.tts_instance = TTS(self.coqui_model_name, gpu=False)
            except Exception as e:
                logger.error(f"Failed to load Coqui: {e}")
                self.tts_instance = None

    def _load_pyttsx3(self):
        if PYTTSX3_AVAILABLE and self.pyttsx3_engine is None:
            try:
                self.pyttsx3_engine = pyttsx3.init()
                voices = self.pyttsx3_engine.getProperty('voices')
                # Try to find a female voice
                for voice in voices:
                    if "female" in voice.name.lower() or "zina" in voice.name.lower():
                        self.pyttsx3_engine.setProperty('voice', voice.id)
                        break
                self.pyttsx3_engine.setProperty('rate', 165)
            except Exception as e:
                logger.error(f"Failed to load pyttsx3: {e}")

    def clean_text(self, text: str) -> str:
        """Strips markdown and limits length for better TTS performance."""
        text = re.sub(r'[\*\#\-\_\>\<\`]', '', text)
        text = text.replace('\n', ' ')
        return text[:300].strip()

    def synthesize(self, text: str) -> bytes:
        """Converts text to audio bytes (WAV)."""
        text = self.clean_text(text)
        if not text:
            return b""

        # Try Coqui first if preferred
        if self.engine_preference == "coqui" and COQUI_AVAILABLE:
            self._load_coqui()
            if self.tts_instance:
                try:
                    start_time = time.time()
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                        tmp_path = tmp.name
                    
                    self.tts_instance.tts_to_file(text=text, file_path=tmp_path)
                    
                    with open(tmp_path, "rb") as f:
                        audio_data = f.read()
                    
                    os.remove(tmp_path)
                    logger.info(f"Coqui TTS ({time.time() - start_time:.2f}s) generated {len(audio_data)} bytes")
                    return audio_data
                except Exception as e:
                    logger.error(f"Coqui Synthesis Error: {e}")

        # Fallback to pyttsx3
        if PYTTSX3_AVAILABLE:
            self._load_pyttsx3()
            if self.pyttsx3_engine:
                try:
                    start_time = time.time()
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                        tmp_path = tmp.name
                    
                    self.pyttsx3_engine.save_to_file(text, tmp_path)
                    self.pyttsx3_engine.runAndWait()
                    
                    # Wait a bit for file to be written/flushed
                    time.sleep(0.1)
                    
                    if os.path.exists(tmp_path):
                        with open(tmp_path, "rb") as f:
                            audio_data = f.read()
                        os.remove(tmp_path)
                        logger.info(f"pyttsx3 TTS ({time.time() - start_time:.2f}s) generated {len(audio_data)} bytes")
                        return audio_data
                except Exception as e:
                    logger.error(f"pyttsx3 Synthesis Error: {e}")

        return b""

# Global singleton
tts = TextToSpeech()
