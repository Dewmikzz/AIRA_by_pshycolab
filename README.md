# ═══ FILE: README.md ═══
# Aira — Psycholab AI Receptionist (v3.0)

Aira is a fully autonomous, local-first AI voice agent built for Psycholab IT Company, Sri Lanka. It uses OpenAI Whisper for Speech-to-Text, Ollama for LLM reasoning, and Coqui TTS for high-quality voice synthesis.

## 🚀 Key Features
- **100% Local**: No data leaves your machine. 100% free open-source models.
- **Dynamic Model Selection**: Auto-detects RAM to pick the best LLM (Llama 3.2, Mistral, Llama 3.1, or TinyLlama).
- **Voice-to-Voice Pipeline**: seamless transcription, brain processing, and speech playback.
- **Modern UI**: Dark-mode web interface with real-time audio visualization.
- **Sri Lanka Context**: Pre-trained on Psycholab's services and callback protocol.

## 🛠️ Tech Stack
- **STT**: `openai-whisper` (base)
- **LLM**: `ollama/llama3.2` (via `ollama` Python library)
- **TTS**: `Coqui-ai/TTS` (VITS model) with `pyttsx3` fallback
- **Backend**: `FastAPI` + `Uvicorn`
- **Frontend**: Vanilla HTML/CSS/JS (No build step)

## 📦 Setup & Installation

### Windows
1. Install [Ollama](https://ollama.com).
2. Install [ffmpeg](https://ffmpeg.org/download.html) (add to PATH).
3. Run `start.bat`.

### Linux/macOS
1. Install [Ollama](https://ollama.com).
2. Install ffmpeg (`sudo apt install ffmpeg` or `brew install ffmpeg`).
3. Run `./start.sh`.

## 🧪 Testing
Run the automated connectivity test:
```bash
python tests/test_talk.py
```

## 📜 License
Built by Antigravity for Psycholab. Proprietary / Open Source (MIT).
