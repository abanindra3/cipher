# Installation Guide

## macOS / MacBook

1. Install Python 3.11 or newer.

If you use Homebrew:

```bash
brew install python
```

2. Open Terminal in the project folder.

```bash
cd "/path/to/build-a-production-quality-ai-voice"
```

3. Install JARVIS:

```bash
chmod +x scripts/*.sh
./scripts/install_macos.sh
```

4. Edit `.env` and add `GEMINI_API_KEY`.

```env
GEMINI_API_KEY=your_gemini_key_here
```

Get a free-tier Gemini key from:

```text
https://aistudio.google.com/app/apikey
```

5. Enroll your voice:

```bash
./.venv/bin/jarvis --enroll-voice
```

Say clearly: `Cipher, this is my voice profile.`

6. Start JARVIS:

```bash
./scripts/run_macos.sh
```

7. Grant macOS permissions when prompted:

- Microphone access for Terminal or your Python executable.
- Accessibility permission if you later add deeper computer-control actions.
- Network access for Gemini, weather, RSS, and search features.

8. Optional startup launch:

```bash
./scripts/register_startup_macos.sh
```

API docs will be available at:

```text
http://127.0.0.1:8765/docs
```

## Windows

1. Install Python 3.11 or newer.
2. Open PowerShell in the project folder.
3. Run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\install_windows.ps1
```

4. Edit `.env` and add `GEMINI_API_KEY`.
5. Enroll your voice:

```powershell
.\.venv\Scripts\jarvis.exe --enroll-voice
```

6. Start JARVIS:

```powershell
.\scripts\run_windows.ps1
```

7. Optional startup launch:

```powershell
.\scripts\register_startup_windows.ps1
```

## Voice Setup

- Wake word: `Cipher`
- Default wake mode uses lightweight local speech recognition.
- Enroll your voice once with `jarvis --enroll-voice`.
- Test speech with `jarvis --test-voice`.
- Test microphone transcription with `jarvis --listen-once`.
- Debug continuous wake detection with `jarvis --voice-debug`.
- If someone else says `Cipher`, JARVIS speaks the configured rejection message and does not execute the command.
- For stronger wake-word performance, set `WAKE_WORD_ENGINE=porcupine` and wire a Porcupine keyword model.

## Gemini Setup

The app uses:

- `gemini-3.5-flash` for reasoning and tool calling by default.
- Free/local microphone transcription through `SpeechRecognition`.
- Local male robotic speech through `pyttsx3`.

These can be changed in `.env`.
