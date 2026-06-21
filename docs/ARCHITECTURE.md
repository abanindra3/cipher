# JARVIS Architecture

```mermaid
flowchart LR
  Mic["Microphone"] --> Wake["Wake word: Cipher"]
  Wake --> Auth["Voice authorization"]
  Auth --> STT["Speech-to-text"]
  STT --> Engine["Assistant Engine"]
  UI["PyQt6 Desktop UI"] --> API["FastAPI REST API"]
  Android["Future Android App"] --> API
  API --> Engine
  Engine --> Memory["SQLite Memory + Conversations"]
  Engine --> Tools["Permissioned Tool Registry"]
  Tools --> OS["Windows Apps / Files / Browser"]
  Tools --> Internet["Weather / RSS / Stocks / Search"]
  Engine --> TTS["Text-to-speech"]
  TTS --> Speaker["Speaker"]
  API --> Notifications["Notifications + Reminders"]
```

## Design

JARVIS is split into isolated layers:

- `desktop`: PyQt6 system tray and desktop UI.
- `backend/api`: FastAPI endpoints for desktop and future Android clients.
- `backend/ai`: OpenAI Responses API orchestration, memory extraction, and prompt policy.
- `backend/tools`: structured tools plus a permission layer.
- `backend/voice`: wake word, voice auth, STT, and TTS adapters.
- `backend/db`: SQLite schema and repository classes.
- `backend/services`: daily briefing and notifications.

The backend binds to `127.0.0.1` by default. Keep it local unless you add authentication and TLS.

