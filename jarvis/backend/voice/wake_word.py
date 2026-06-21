from __future__ import annotations

import threading
import time
from collections.abc import Callable
from pathlib import Path
import re
from difflib import SequenceMatcher

from jarvis.backend.core.config import settings
from jarvis.backend.core.logging import get_logger
from jarvis.backend.voice.audio_io import MicrophoneRecorder
from jarvis.backend.voice.stt import SpeechToText
from jarvis.backend.voice.voice_auth import VoiceAuthenticator

logger = get_logger(__name__)


class WakeWordListener:
    def __init__(
        self,
        on_wake: Callable[[Path, str | None], None],
        on_unauthorized: Callable[[], None] | None = None,
        recorder: MicrophoneRecorder | None = None,
        auth: VoiceAuthenticator | None = None,
    ) -> None:
        self.on_wake = on_wake
        self.on_unauthorized = on_unauthorized
        self.recorder = recorder or MicrophoneRecorder()
        self.stt = SpeechToText()
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
        print(f"JARVIS wake listener active. Say '{settings.wake_word}' plus a command.", flush=True)
        while not self._stop.is_set():
            try:
                wake_audio = self.recorder.record_wake_phrase()
                heard = self.stt.transcribe(wake_audio)
                if settings.wake_debug:
                    print(f"Heard: {heard or '[nothing recognized]'}", flush=True)
                logger.info("Wake phrase heard: %s", heard)
                if not self._contains_wake_word(heard):
                    time.sleep(0.1)
                    continue
                if not self.auth.is_authorized(wake_audio):
                    logger.info("Wake word heard, but speaker was not authorized.")
                    if self.on_unauthorized:
                        self.on_unauthorized()
                    continue
                inline_command = self._command_after_wake(heard)
                self.on_wake(wake_audio, inline_command or None)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Wake listener paused after error: %s", exc)
                time.sleep(3)

    def _command_after_wake(self, text: str) -> str:
        aliases = self._wake_aliases()
        matches: list[re.Match[str]] = []
        for alias in aliases:
            matches.extend(re.finditer(re.escape(alias), text, re.IGNORECASE))
        if matches:
            latest = max(matches, key=lambda match: match.end())
            command = text[latest.end() :]
            return command.strip(" ,.:;-")

        words = re.findall(r"[a-zA-Z]+", text)
        for index, word in enumerate(words):
            if self._is_wake_word(word):
                return " ".join(words[index + 1 :]).strip()
        return ""

    def _contains_wake_word(self, text: str) -> bool:
        if not text:
            return False
        lowered = text.lower()
        if any(alias in lowered for alias in self._wake_aliases()):
            return True
        return any(self._is_wake_word(word) for word in re.findall(r"[a-zA-Z]+", lowered))

    def _is_wake_word(self, word: str) -> bool:
        normalized = word.lower().strip()
        if normalized in self._wake_aliases():
            return True
        return SequenceMatcher(None, normalized, settings.wake_word.lower()).ratio() >= 0.72

    def _wake_aliases(self) -> list[str]:
        aliases = [settings.wake_word, *settings.wake_word_aliases.split(",")]
        return [alias.strip().lower() for alias in aliases if alias.strip()]


def strip_wake_word(text: str) -> str:
    listener = WakeWordListener(lambda _audio, _command: None)
    if not listener._contains_wake_word(text):
        return ""
    command = listener._command_after_wake(text)
    if command:
        return command
    aliases = listener._wake_aliases()
    words = [word for word in re.findall(r"[a-zA-Z0-9]+", text) if word.lower() not in aliases]
    return " ".join(words).strip()
