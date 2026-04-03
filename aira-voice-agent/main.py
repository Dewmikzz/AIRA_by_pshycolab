# ═══ FILE: main.py ═══
# Purpose: FastAPI WebSocket Orchestrator with Binary Streaming Support
# Handles: Binary Audio Chunks & JSON Command Messages

import os
import base64
import uuid
import json
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List, Optional

class VoiceRequest(BaseModel):
    audio: Optional[str] = None # Base64 encoded audio
    text: Optional[str] = None # Direct text input
    history: List[dict] = []
    session_id: Optional[str] = "default"

# Import Production Cloud Modules
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
    try:
        # Check for direct text first (e.g. for greetings)
        transcript = request.text
        logger.info(f"API Request | Session: {request.session_id} | History: {len(request.history)} | Text: {transcript}")
        
        if not transcript and request.audio:
            # 1. Decode Audio
            actual_audio = base64.b64decode(request.audio)
            
            # 2. STT
            transcript = await stt.transcribe(actual_audio)
            if transcript in ["__silence__", "__error__"]:
                return {"error": "No speech detected", "history": request.history}
            
        if not transcript:
            return {"error": "No input provided", "history": request.history}
            
        # 3. Agent (Stateless)
        reply_text, updated_history = await agent.ask(transcript, history=request.history)
        
        # 4. TTS
        reply_audio = await tts.synthesize(reply_text)
        reply_b64 = base64.b64encode(reply_audio).decode("utf-8") if reply_audio else ""
        
        return {
            "transcript": transcript,
            "reply_text": reply_text,
            "reply_audio": reply_b64,
            "history": updated_history
        }
    except Exception as e:
        logger.error(f"API Error: {e}")
        return {"error": str(e)}

@app.websocket("/voice-call")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = str(uuid.uuid4())
    logger.info(f"New Voice Call started: {session_id}")
    
    try:
        # 1. Send Aira's greeting immediately!
        greeting_text, _ = await agent.ask("greet", session_id)
        greeting_audio = await tts.synthesize(greeting_text)
        greeting_b64 = base64.b64encode(greeting_audio).decode("utf-8") if greeting_audio else ""
        
        await websocket.send_json({
            "type": "greeting",
            "text": greeting_text,
            "audio": greeting_b64,
            "session_id": session_id
        })
        
        # 2. Main Voice Loop
        audio_buffer = bytearray()
        
        while True:
            # [FIX] Handle both binary chunks (audio) and text (commands)
            msg = await websocket.receive()
            
            if "bytes" in msg:
                # Direct Binary PCM from Frontend
                audio_buffer.extend(msg["bytes"])
                
                # Simple threshold for processing (e.g. 500ms of audio)
                if len(audio_buffer) > 16000: # 1 second at 16k mono
                    # Check for silence or send for processing
                    pass 

            elif "text" in msg:
                data = json.loads(msg["text"])
                
                if data["type"] == "end_of_speech":
                    if len(audio_buffer) < 500:
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
                    await websocket.send_json({"type": "reply_text", "text": reply_text})
                    
                    await websocket.send_json({"type": "status", "state": "speaking"})
                    reply_audio = await tts.synthesize(reply_text)
                    reply_b64 = base64.b64encode(reply_audio).decode("utf-8") if reply_audio else ""
                    
                    await websocket.send_json({
                        "type": "reply_audio",
                        "audio": reply_b64
                    })
                    await websocket.send_json({"type": "status", "state": "listening"})

                elif data["type"] == "end_call":
                    logger.info(f"User hanging up: {session_id}")
                    memory.reset(session_id)
                    break

    except WebSocketDisconnect:
        logger.info(f"Disconnected Session: {session_id}")
        memory.reset(session_id)
    except Exception as e:
        logger.error(f"WebSocket Error: {e}")
        try:
            await websocket.send_json({"type": "error", "message": f"Engine Error: {str(e)}"})
        except: pass
        memory.reset(session_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
