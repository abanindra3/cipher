# JARVIS: Cipher Voice Assistant

JARVIS is a desktop-first AI companion for Windows and macOS. It runs from the system tray/menu bar, keeps a local memory database, exposes REST APIs for future Android integration, and uses structured tool calling for safe computer control.

## Features

- Always-running PyQt6 desktop app with system tray behavior.
- Wake word architecture for `Cipher`.
- Speech-to-text, GPT reasoning, and text-to-speech adapters.
- Local SQLite memory for durable personal facts.
- Permissioned tools for apps, websites, Google, YouTube, files, folders, reminders, weather, stocks, RSS, and sports lookup.
- Daily briefing endpoint for “Good morning Jarvis”.
- Notification and reminder services.
- Future-ready Android REST command endpoint.
- Local fallback mode when `OPENAI_API_KEY` is not set.

## Quick Start

### macOS / MacBook

```bash
chmod +x scripts/*.sh
./scripts/install_macos.sh
./scripts/run_macos.sh
```

### Windows

```powershell
.\scripts\install_windows.ps1
.\scripts\run_windows.ps1
```

Then add your key to `.env`:

```env
OPENAI_API_KEY=sk-...
```

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
- “Cipher, launch VS Code”
- “Cipher, search UPSC current affairs”
- “Cipher, good morning Jarvis”
- “Cipher, remember I am preparing for UPSC 2027”
- “Cipher, remember I want to become an IPS officer”

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Installation](docs/INSTALLATION.md)
- [Database Schema](docs/DATABASE_SCHEMA.md)
- [API Documentation](docs/API.md)

## Security Model

JARVIS never executes raw shell commands from user text. All actions go through named structured tools and a permission layer. Destructive or disruptive actions, such as closing apps, require confirmation.

Keep the API bound to `127.0.0.1` unless you add authentication, TLS, and network access controls.

## OpenAI API Notes

This project follows the current OpenAI docs for Responses API function/tool calling, speech-to-text with `gpt-4o-transcribe`, and text-to-speech with `gpt-4o-mini-tts`.

Sources:

- [Function calling](https://developers.openai.com/api/docs/guides/function-calling)
- [Speech to text](https://developers.openai.com/api/docs/guides/speech-to-text)
- [Text to speech](https://developers.openai.com/api/docs/guides/text-to-speech)
