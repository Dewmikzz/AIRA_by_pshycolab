# ═══ FILE: stt.py ═══
# Purpose: Speech-to-Text using OpenAI Whisper
# Inputs: Audio file (bytes) in various formats (WebM, WAV, etc.)
# Outputs: Transcribed text string

import whisper
import os
import tempfile
import time
from pydub import AudioSegment
import logging

# [THINK] Browsers record in WebM (Opus), but Whisper prefers WAV/MP3.
# [THINK] ffmpeg must be on the path for pydub to work correctly.
# [THINK] '__silence__' return helps main.py skip LLM calls on empty noise.

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AiraSTT")

class SpeechToText:
    def __init__(self, model_name: str = "base"):
        self.model_name = model_name
        self.model = None

    def load_model(self):
        """Loads the Whisper model into memory."""
        if self.model is None:
            logger.info(f"Loading Whisper model: {self.model_name}...")
            start_time = time.time()
            self.model = whisper.load_model(self.model_name)
            logger.info(f"Whisper loaded in {time.time() - start_time:.2f}s")

    def transcribe(self, audio_bytes: bytes, file_ext: str = "webm") -> str:
        """Converts audio bytes to text."""
        self.load_model()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as temp_audio:
            temp_audio.write(audio_bytes)
            temp_path = temp_audio.name

        try:
            # Convert to wav for consistency if not already wav
            if file_ext != "wav":
                wav_path = temp_path.replace(f".{file_ext}", ".wav")
                audio = AudioSegment.from_file(temp_path)
                audio.export(wav_path, format="wav")
                os.remove(temp_path)
                temp_path = wav_path

            start_time = time.time()
            result = self.model.transcribe(temp_path, fp16=False) # fp16=False for CPU stability
            text = result.get("text", "").strip()
            
            logger.info(f"Transcription ({time.time() - start_time:.2f}s): {text}")
            
            if len(text) < 3:
                return "__silence__"
            return text

        except Exception as e:
            logger.error(f"STT Error: {e}")
            return "__error__"
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

# Global singleton
stt = SpeechToText(model_name=os.getenv("WHISPER_MODEL", "base"))
