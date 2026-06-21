from __future__ import annotations

import argparse
import threading
from pathlib import Path

import uvicorn

from jarvis.backend.api.app import create_app
from jarvis.backend.core.config import settings
from jarvis.backend.core.logging import configure_logging, get_logger
from jarvis.backend.voice import TextToSpeech, VoicePipeline, WakeWordListener
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

    def on_wake(audio_path: Path) -> None:
        result = pipeline.process_audio(audio_path)
        logger.info("Voice command handled: %s", result.get("transcript"))

    def on_unauthorized() -> None:
        tts.speak("I heard the wake word, but this voice is not authorized.")

    listener = WakeWordListener(on_wake=on_wake, on_unauthorized=on_unauthorized)
    listener.start()
    return listener


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the JARVIS assistant.")
    parser.add_argument("--api-only", action="store_true", help="Run only the FastAPI backend.")
    parser.add_argument("--gui-only", action="store_true", help="Run only the PyQt desktop UI.")
    args = parser.parse_args()

    configure_logging()

    if args.api_only:
        run_api()
        return

    if not args.gui_only:
        thread = threading.Thread(target=run_api, name="jarvis-api", daemon=True)
        thread.start()
        logger.info("API server starting at http://%s:%s", settings.app_host, settings.app_port)

    start_voice_listener()
    run_desktop()


if __name__ == "__main__":
    main()
