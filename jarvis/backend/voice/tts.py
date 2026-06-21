from __future__ import annotations

import platform
import shutil
import subprocess
from pathlib import Path

import pyttsx3

from jarvis.backend.core.config import settings


class TextToSpeech:
    def __init__(self) -> None:
        self.use_macos_say = platform.system().lower() == "darwin" and shutil.which("say")
        self.engine = None
        if not self.use_macos_say:
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", settings.tts_rate)
            self.engine.setProperty("volume", settings.tts_volume)
            self._select_male_voice()

    def speak(self, text: str) -> Path | None:
        spoken = self._robotic_text(text)
        if self.use_macos_say:
            subprocess.run(
                ["say", "-v", "Daniel", "-r", str(settings.tts_rate), spoken],
                check=False,
            )
            return None
        if self.engine:
            self.engine.say(spoken)
            self.engine.runAndWait()
        return None

    def _select_male_voice(self) -> None:
        if not self.engine:
            return
        voices = self.engine.getProperty("voices") or []
        preferred = ["daniel", "alex", "fred", "ralph", "tom", "male"]
        for voice in voices:
            name = f"{getattr(voice, 'name', '')} {getattr(voice, 'id', '')}".lower()
            if any(token in name for token in preferred):
                self.engine.setProperty("voice", voice.id)
                return

    def _robotic_text(self, text: str) -> str:
        return " ".join(text.replace(".", ". ").replace(",", ", ").split())
