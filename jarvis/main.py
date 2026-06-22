from __future__ import annotations

import argparse
import threading
import time
from datetime import datetime
from pathlib import Path

import uvicorn

from jarvis.backend.api.app import create_app
from jarvis.backend.core.config import settings
from jarvis.backend.core.logging import configure_logging, get_logger
from jarvis.backend.db.repositories import NotificationRepository
from jarvis.backend.voice import TextToSpeech, VoicePipeline, WakeWordListener
from jarvis.backend.voice.audio_io import MicrophoneRecorder
from jarvis.backend.voice.stt import SpeechToText
from jarvis.backend.voice.wake_word import strip_wake_word
from jarvis.backend.voice.voice_auth import VoiceAuthenticator
from jarvis.desktop.app import run_desktop

logger = get_logger(__name__)


def run_api() -> None:
    uvicorn.run(
        create_app(),
        host=settings.app_host,
        port=settings.app_port,
        log_level=settings.log_level.lower(),
    )


def start_voice_listener() -> WakeWordListener:
    pipeline = VoicePipeline()
    tts = TextToSpeech()

    def on_wake(audio_path: Path, command_text: str | None) -> None:
        if command_text:
            result = pipeline.process_text(command_text)
        else:
            tts.speak("Yes sir.")
            result = pipeline.capture_respond_speak()
        logger.info("Voice command handled: %s", result.get("transcript"))

    def on_unauthorized() -> None:
        if not settings.voice_profile_path.exists():
            tts.speak("Voice profile missing. Please enroll your voice first.")
        else:
            tts.speak(settings.voice_reject_message)

    listener = WakeWordListener(on_wake=on_wake, on_unauthorized=on_unauthorized)
    listener.start()
    return listener


def start_reminder_watcher() -> threading.Thread:
    repo = NotificationRepository()
    tts = TextToSpeech()

    def loop() -> None:
        while True:
            try:
                for reminder in repo.due_reminders(datetime.now()):
                    text = reminder["text"]
                    tts.speak(f"Reminder, boss. {text}")
                    repo.add("reminder", "Reminder", text)
                    repo.mark_reminder_delivered(int(reminder["id"]))
            except Exception as exc:  # noqa: BLE001
                logger.warning("Reminder watcher error: %s", exc)
            time.sleep(20)

    thread = threading.Thread(target=loop, name="reminder-watcher", daemon=True)
    thread.start()
    return thread


def run_voice_debug() -> None:
    recorder = MicrophoneRecorder()
    stt = SpeechToText()
    tts = TextToSpeech()
    pipeline = VoicePipeline()
    print(f"Voice debug active. Say '{settings.wake_word} open Safari' or press Ctrl+C.", flush=True)
    while True:
        audio = recorder.record_wake_phrase()
        transcript = stt.transcribe(audio)
        print(f"Heard: {transcript or '[nothing recognized]'}", flush=True)
        command = strip_wake_word(transcript)
        if not command:
            continue
        print(f"Wake detected. Command: {command or '[none]'}", flush=True)
        if command:
            pipeline.process_text(command)
        else:
            tts.speak("Yes sir.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the JARVIS assistant.")
    parser.add_argument("--api-only", action="store_true", help="Run only the FastAPI backend.")
    parser.add_argument("--gui-only", action="store_true", help="Run only the PyQt desktop UI.")
    parser.add_argument("--enroll-voice", action="store_true", help="Record your voice profile for wake-word authorization.")
    parser.add_argument("--test-voice", action="store_true", help="Speak a short test sentence.")
    parser.add_argument("--listen-once", action="store_true", help="Record once and print the transcript for microphone testing.")
    parser.add_argument("--voice-debug", action="store_true", help="Run terminal-only wake-word debugging.")
    args = parser.parse_args()

    configure_logging()

    if args.enroll_voice:
        print("Speak clearly for 8 seconds. Say: Cipher, this is my voice profile.")
        audio = MicrophoneRecorder(phrase_time_limit=8).record_command()
        VoiceAuthenticator().enroll(audio)
        print(f"Voice profile saved to {settings.voice_profile_path}")
        return

    if args.test_voice:
        TextToSpeech().speak("JARVIS voice systems online. I am ready, sir.")
        return

    if args.listen_once:
        print("Listening for 6 seconds. Speak now.")
        audio = MicrophoneRecorder(phrase_time_limit=6).record_command()
        transcript = SpeechToText().transcribe(audio)
        print(f"Transcript: {transcript or '[nothing recognized]'}")
        return

    if args.voice_debug:
        run_voice_debug()
        return

    if args.api_only:
        run_api()
        return

    if not args.gui_only:
        thread = threading.Thread(target=run_api, name="jarvis-api", daemon=True)
        thread.start()
        logger.info("API server starting at http://%s:%s", settings.app_host, settings.app_port)

    start_reminder_watcher()
    start_voice_listener()
    run_desktop()


if __name__ == "__main__":
    main()
