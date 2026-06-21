from __future__ import annotations

import tempfile
from pathlib import Path

import pyttsx3
from openai import OpenAI

from jarvis.backend.core.config import settings


class TextToSpeech:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    def speak(self, text: str) -> Path | None:
        if self.client:
            return self._speak_openai(text)
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        return None

    def _speak_openai(self, text: str) -> Path:
        path = Path(tempfile.gettempdir()) / "jarvis_response.mp3"
        with self.client.audio.speech.with_streaming_response.create(
            model=settings.openai_tts_model,
            voice=settings.openai_tts_voice,
            input=text,
            instructions="Speak like a composed, warm personal AI assistant.",
        ) as response:
            response.stream_to_file(path)
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        return path

