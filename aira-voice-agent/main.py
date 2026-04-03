# ═══ FILE: main.py ═══
# Purpose: FastAPI WebSocket Orchestrator with Enterprise Stability & Binary Support
# Handles: Binary Audio Chunks & JSON Command Messages

import os
import base64
import uuid
import json
import logging
import traceback
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List, Optional

# --- [MODELS] ---
class VoiceRequest(BaseModel):
    audio: Optional[str] = None # Base64 encoded audio
    text: Optional[str] = None # Direct text input
    history: List[dict] = []
    session_id: Optional[str] = "default"

# --- [SERVICES] ---
from stt import stt
from tts import tts
from agent import agent
from memory import memory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AiraMain")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Aira Elite Pipeline is online.")
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

@app.post("/api/voice")
async def voice_api(request: VoiceRequest):
    """Stateless Voice API for High-Velocity Real-Time Conversation."""
    try:
        # 1. Input Processing
        transcript = request.text
        logger.info(f"API Request | Session: {request.session_id} | Hist: {len(request.history)}")
        
        if not transcript and request.audio:
            actual_audio = base64.b64decode(request.audio)
            transcript = await stt.transcribe(actual_audio)
            
            if transcript in ["__silence__", "__error__"]:
                return {"error": "Silence", "history": request.history}
            
        if not transcript:
            return {"error": "No Input", "history": request.history}
            
        # 2. Intelligence (Llama 3.3 70B Core)
        reply_text, updated_history = await agent.ask(transcript, history=request.history)
        logger.info(f"API Reply | {reply_text[:60]}...")
        
        # 3. Neural Synthesis (Premium Cloud TTS)
        reply_audio = await tts.synthesize(reply_text)
        reply_b64 = base64.b64encode(reply_audio).decode("utf-8") if reply_audio else ""
        
        return {
            "transcript": transcript,
            "reply_text": reply_text,
            "reply_audio": reply_b64,
            "history": updated_history
        }
    except Exception as e:
        # [CRITICAL] Log full traceback to identify random exits
        logger.error(f"API Recovery Error: {e}")
        traceback.print_exc()
        return {"error": "Stability Recovery triggered", "details": str(e)}

@app.websocket("/voice-call")
async def websocket_endpoint(websocket: WebSocket):
    """Stateful WebSocket for Dedicated Real-Time Sessions."""
    await websocket.accept()
    session_id = str(uuid.uuid4())
    logger.info(f"Elite Neural Call Started: {session_id}")
    
    try:
        # 1. Neural Handshake
        greeting_text, _ = await agent.ask("greet", session_id)
        logger.info(f"Neural Handshake: {greeting_text[:50]}...")
        
        greeting_audio = await tts.synthesize(greeting_text)
        greeting_b64 = base64.b64encode(greeting_audio).decode("utf-8") if greeting_audio else ""
        
        await websocket.send_json({
            "type": "greeting",
            "text": greeting_text,
            "audio": greeting_b64,
            "session_id": session_id
        })
        
        # 2. Interaction Loop
        audio_buffer = bytearray()
        
        while True:
            msg = await websocket.receive()
            
            if "bytes" in msg:
                audio_buffer.extend(msg["bytes"])
                if len(audio_buffer) > 16000: # 1s simple gating
                    pass 

            elif "text" in msg:
                data = json.loads(msg["text"])
                
                if data["type"] == "end_of_speech":
                    if len(audio_buffer) < 1000:
                        audio_buffer = bytearray()
                        continue

                    await websocket.send_json({"type": "status", "state": "thinking"})
                    transcript = await stt.transcribe(bytes(audio_buffer))
                    audio_buffer = bytearray()
                    
                    if transcript in ["__silence__", "__error__"]:
                        await websocket.send_json({"type": "status", "state": "listening"})
                        continue
                    
                    await websocket.send_json({"type": "transcript", "text": transcript})
                    reply_text, _ = await agent.ask(transcript, session_id)
                    
                    await websocket.send_json({"type": "status", "state": "speaking"})
                    reply_audio = await tts.synthesize(reply_text)
                    reply_b64 = base64.b64encode(reply_audio).decode("utf-8") if reply_audio else ""
                    
                    await websocket.send_json({
                        "type": "reply_text", "text": reply_text,
                        "type": "reply_audio", "audio": reply_b64
                    })
                    await websocket.send_json({"type": "status", "state": "listening"})

                elif data["type"] == "end_call":
                    logger.info(f"User hanging up: {session_id}")
                    memory.reset(session_id)
                    break

    except WebSocketDisconnect:
        logger.info(f"Neural Node Disconnected: {session_id}")
        memory.reset(session_id)
    except Exception as e:
        logger.error(f"WebSocket System Crash: {e}")
        traceback.print_exc()
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except: pass
        memory.reset(session_id)

if __name__ == "__main__":
    import uvicorn
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except SystemExit:
        logger.info("Aira shutting down gracefully.")
    except Exception as e:
        logger.error(f"CRITICAL PROCESS CRASH: {e}")
        traceback.print_exc()
