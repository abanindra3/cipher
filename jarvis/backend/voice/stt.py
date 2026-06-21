from __future__ import annotations

from pathlib import Path

import speech_recognition as sr


class SpeechToText:
    def __init__(self) -> None:
        self.recognizer = sr.Recognizer()

    def transcribe(self, audio_path: Path) -> str:
        with sr.AudioFile(str(audio_path)) as source:
            audio = self.recognizer.record(source)
        try:
            return self.recognizer.recognize_google(audio).strip()
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            return ""
