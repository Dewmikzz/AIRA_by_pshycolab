# AIRA · Production-Grade AI Voice Call (v4.0)

Aira is a professional, high-fidelity AI voice receptionist for **Psycholab**, built with a focus on real-time, zero-latency communication. It uses elite Cloud APIs to achieve sub-second response times in a natural "phone call" environment.

## 🚀 The Stack
- **STT**: [Groq](https://groq.com/) — Whisper-Large-V3 (Real-time transcription).
- **LLM**: [OpenRouter](https://openrouter.ai/) — Llama-3.1-8B-Instruct (High-speed cognition).
- **TTS**: [Edge-TTS](https://github.com/rany2/edge-tts) — Microsoft Jenny Neural Voice (Zero cost, high quality).
- **Transport**: FastAPI + WebSockets (Bi-directional streaming).
- **Frontend**: Vanilla JS + Web Audio API + Voice Activity Detection (VAD).

## 🛠️ Quick Start (3 Steps Only)

### 1. Get Your Free API Keys
-   Go to [groq.com](https://groq.com/), create an account, and generate an API key.
-   Go to [openrouter.ai](https://openrouter.ai/), create an account, and generate an API key.

### 2. Configure Environment
Create a `.env` file from the example:
```bash
copy .env.example .env
```
Open `.env` and paste your keys:
```env
GROQ_API_KEY="gsk_..."
OPENROUTER_API_KEY="sk-or-..."
```

### 3. Launch & Call
Run the one-click launcher:
```bash
./start.bat
```
Visit **[http://localhost:8000](http://localhost:8000)** and click the green **"Start Call"** button.

## 📞 Call Features
-   **Auto-Greeting**: Aira greets you immediately when the call starts.
-   **Real-Time VAD**: The app automatically detects when you stop speaking to trigger the AI response.
-   **Voice Aura**: Visual feedback pulses when Aira speaks.
-   **Call Log**: View the live transcript of the call.
-   **Malaysia Identity**: Specialized knowledge about Psycholab's Malaysian office and services.

---
*Built for Psycholab by AIRA Engineering Team.*
