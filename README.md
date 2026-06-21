# JARVIS: Cipher Voice Assistant

JARVIS is a desktop-first AI companion for Windows and macOS. It runs from the system tray/menu bar, keeps a local memory database, exposes REST APIs for future Android integration, and uses structured tool calling for safe computer control.

## Features

- Always-running PyQt6 desktop app with system tray behavior.
- Wake word architecture for `Cipher`.
- Free speech recognition, Gemini reasoning, and local male robotic text-to-speech.
- Local SQLite memory for durable personal facts.
- Permissioned tools for apps, websites, Google, YouTube, files, folders, reminders, weather, stocks, RSS, and sports lookup.
- Daily briefing endpoint for “Good morning Jarvis”.
- Notification and reminder services.
- Future-ready Android REST command endpoint.
- Local fallback mode when `GEMINI_API_KEY` is not set.

## Quick Start

### macOS / MacBook

```bash
chmod +x scripts/*.sh
./scripts/install_macos.sh
open .env
./.venv/bin/jarvis --enroll-voice
./scripts/run_macos.sh
```

### Windows

```powershell
.\scripts\install_windows.ps1
.\scripts\run_windows.ps1
```

Then add your key to `.env`:

```env
GEMINI_API_KEY=your_gemini_key_here
```

Get a free-tier Gemini key from [Google AI Studio](https://aistudio.google.com/app/apikey).

## Run API Only

macOS:

```bash
./.venv/bin/jarvis --api-only
```

Windows:

```powershell
.\.venv\Scripts\jarvis.exe --api-only
```

Open API docs at:

```text
http://127.0.0.1:8765/docs
```

## Example Commands

- “Cipher, open Chrome”
- “Cipher, open Safari”
- “Cipher, search in Safari UPSC current affairs”
- “Cipher, launch VS Code”
- “Cipher, search UPSC current affairs”
- “Cipher, good morning Jarvis”
- “Cipher, remember I am preparing for UPSC 2027”
- “Cipher, remember I want to become an IPS officer”
- “Cipher, open Spotify”
- “Cipher, what is the weather in Kolkata?”
- “Cipher, call 9876543210 on FaceTime”
- “Cipher, send WhatsApp message to 919876543210 saying I will call later”

## Voice Checks

If text works but voice does not:

```bash
./.venv/bin/jarvis --test-voice
./.venv/bin/jarvis --listen-once
./.venv/bin/jarvis --enroll-voice
./scripts/run_macos.sh
```

On macOS, allow microphone access for Terminal/Python in System Settings.

For continuous wake-word debugging without the GUI:

```bash
./.venv/bin/jarvis --voice-debug
```

This prints every recognized chunk as `Heard: ...`, so if macOS hears `safer` or `cypher` instead of `cipher`, you can still see what happened.

## Calls And Messages

JARVIS can open FaceTime, Messages, and WhatsApp drafts from voice commands. macOS may still ask permission if you ask for contact-name lookup or deeper automation. Using phone numbers avoids Contacts access:

```text
Cipher call 9876543210 on FaceTime
Cipher send WhatsApp message to 919876543210 saying I will call later
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Installation](docs/INSTALLATION.md)
- [Database Schema](docs/DATABASE_SCHEMA.md)
- [API Documentation](docs/API.md)

## Security Model

JARVIS never executes raw shell commands from user text. All actions go through named structured tools and a permission layer. Destructive or disruptive actions, such as closing apps, require confirmation.

Keep the API bound to `127.0.0.1` unless you add authentication, TLS, and network access controls.

## Gemini API Notes

This project uses the Gemini `generateContent` API with function declarations and function responses. Speech recognition uses the local microphone plus the free Google recognizer provided by `SpeechRecognition`; speech output uses local `pyttsx3` with a male robotic voice preference.

Sources:

- [Gemini function calling](https://ai.google.dev/gemini-api/docs/function-calling)
- [Gemini generateContent API](https://ai.google.dev/api/generate-content)
