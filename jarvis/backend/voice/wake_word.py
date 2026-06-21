from __future__ import annotations

import threading
import time
from collections.abc import Callable
from pathlib import Path

from jarvis.backend.core.config import settings
from jarvis.backend.core.logging import get_logger
from jarvis.backend.voice.audio_io import MicrophoneRecorder
from jarvis.backend.voice.voice_auth import VoiceAuthenticator

logger = get_logger(__name__)


class WakeWordListener:
    def __init__(
        self,
        on_wake: Callable[[Path], None],
        on_unauthorized: Callable[[], None] | None = None,
        recorder: MicrophoneRecorder | None = None,
        auth: VoiceAuthenticator | None = None,
    ) -> None:
        self.on_wake = on_wake
        self.on_unauthorized = on_unauthorized
        self.recorder = recorder or MicrophoneRecorder()
        self.auth = auth or VoiceAuthenticator()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, name="wake-word", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def _loop(self) -> None:
        logger.info("Wake listener started for '%s'", settings.wake_word)
        while not self._stop.is_set():
            try:
                heard = self.recorder.recognize_local_text()
                if settings.wake_word.lower() not in heard.lower():
                    time.sleep(0.1)
                    continue
                command_audio = self.recorder.record_command()
                if not self.auth.is_authorized(command_audio):
                    logger.info("Wake word heard, but speaker was not authorized.")
                    if self.on_unauthorized:
                        self.on_unauthorized()
                    continue
                self.on_wake(command_audio)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Wake listener paused after error: %s", exc)
                time.sleep(3)
