from __future__ import annotations

from pathlib import Path

from openai import OpenAI

from jarvis.backend.core.config import settings


class SpeechToText:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    def transcribe(self, audio_path: Path) -> str:
        if not self.client:
            return ""
        with audio_path.open("rb") as audio_file:
            result = self.client.audio.transcriptions.create(
                model=settings.openai_transcribe_model,
                file=audio_file,
                response_format="text",
            )
        return str(result).strip()

