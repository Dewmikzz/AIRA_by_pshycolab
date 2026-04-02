# ═══ FILE: main.py ═══
# Purpose: FastAPI application and orchestration pipeline
# Inputs: HTTP requests (audio, JSON)
# Outputs: JSON response with audio data

import os
import base64
import uuid
import time
import logging
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager

# Import internal modules
from health import get_status
from memory import memory
from stt import stt
from tts import tts
from agent import agent

# [THINK] Why asynccontextmanager? Pre-loading models makes the first click much faster.
# [THINK] CORS is needed for local development testing (8000 vs 8080 etc).
# [THINK] base64 audio return is the most robust way to play on browser without complex streaming.

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AiraMain")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup sequence
    logger.info("Starting Aira pipeline...")
    # Pre-load Whisper
    stt.load_model()
    # Ping Ollama
    status = get_status()
    if not status["ollama_online"]:
        logger.warning("Ollama is not running! Responses will be fallbacks.")
    # Warm up TTS
    tts.synthesize("Hello")
    logger.info("Aira is ready.")
    yield
    # Shutdown sequence
    memory.stop_backup = True

app = FastAPI(lifespan=lifespan, title="Aira Voice Agent")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serves static frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    """Serves the index.html."""
    return FileResponse("static/index.html")

@app.get("/health")
async def health():
    """Returns the system health status."""
    return get_status()

@app.get("/greet")
async def greet(session_id: str = Query(default=None)):
    """Returns Aira's opening audio sequence."""
    if not session_id:
        session_id = str(uuid.uuid4())
    
    text = agent.ask("greet", session_id)
    audio_bytes = tts.synthesize(text)
    audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
    
    return {
        "text": text,
        "audio_base64": audio_base64,
        "session_id": session_id
    }

@app.post("/talk")
async def talk(
    audio: UploadFile = File(...),
    session_id: str = Form(...)
):
    """Voice-to-Voice pipeline primary endpoint."""
    start_time = time.time()
    
    # Read audio bytes
    audio_bytes = await audio.read()
    file_ext = audio.filename.split(".")[-1] if "." in audio.filename else "webm"
    
    # 1. Pipeline Segment: STT
    transcript = stt.transcribe(audio_bytes, file_ext=file_ext)
    
    if transcript == "__silence__":
        return {"transcript": "", "reply": "I didn't catch that, please try again", "audio_base64": "", "duration": 0}
    
    if transcript == "__error__":
        raise HTTPException(status_code=500, detail="Transcription failed")

    # 2. Pipeline Segment: Agent (LLM)
    reply = agent.ask(transcript, session_id)

    # 3. Pipeline Segment: TTS
    audio_output = tts.synthesize(reply)
    audio_base64 = base64.b64encode(audio_output).decode("utf-8")

    duration = time.time() - start_time
    logger.info(f"Total loop duration: {duration:.2f}s")

    return {
        "transcript": transcript,
        "reply": reply,
        "audio_base64": audio_base64,
        "duration_ms": int(duration * 1000)
    }

@app.get("/reset/{session_id}")
async def reset_session(session_id: str):
    """Clears history for a specific session."""
    memory.reset(session_id)
    return {"status": "cleared", "session_id": session_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
