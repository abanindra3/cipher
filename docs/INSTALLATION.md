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

4. Edit `.env` and add `OPENAI_API_KEY`.

```env
OPENAI_API_KEY=your_api_key_here
```

5. Start JARVIS:

```bash
./scripts/run_macos.sh
```

6. Grant macOS permissions when prompted:

- Microphone access for Terminal or your Python executable.
- Accessibility permission if you later add deeper computer-control actions.
- Network access for OpenAI, weather, RSS, and search features.

7. Optional startup launch:

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

4. Edit `.env` and add `OPENAI_API_KEY`.
5. Start JARVIS:

```powershell
.\scripts\run_windows.ps1
```

6. Optional startup launch:

```powershell
.\scripts\register_startup_windows.ps1
```

## Voice Setup

- Wake word: `Cipher`
- Default wake mode uses lightweight local speech recognition.
- For stronger wake-word performance, set `WAKE_WORD_ENGINE=porcupine` and wire a Porcupine keyword model.
- For true “only my voice” behavior, replace `VoiceAuthenticator` with a production speaker-verification model and enroll your profile.

## OpenAI Setup

The app uses:

- `gpt-5.5` for reasoning by default.
- `gpt-4o-transcribe` for speech-to-text.
- `gpt-4o-mini-tts` for text-to-speech.

These can be changed in `.env`.
