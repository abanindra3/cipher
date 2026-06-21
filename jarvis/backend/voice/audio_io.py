from __future__ import annotations

import tempfile
import wave
from pathlib import Path

import numpy as np
import speech_recognition as sr
import sounddevice as sd

from jarvis.backend.core.config import settings


class MicrophoneRecorder:
    def __init__(self, phrase_time_limit: int = 8, sample_rate: int = 16_000) -> None:
        self.recognizer = sr.Recognizer()
        self.phrase_time_limit = phrase_time_limit
        self.sample_rate = sample_rate

    def record_command(self) -> Path:
        path = Path(tempfile.gettempdir()) / "jarvis_command.wav"
        self._record_wav(path, self.phrase_time_limit)
        return path

    def record_wake_phrase(self) -> Path:
        path = Path(tempfile.gettempdir()) / "jarvis_wake_check.wav"
        self._record_wav(path, settings.wake_listen_seconds)
        return path

    def recognize_local_text(self) -> str:
        path = self.record_wake_phrase()
        with sr.AudioFile(str(path)) as source:
            audio = self.recognizer.record(source)
        try:
            return self.recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return ""

    def _record_wav(self, path: Path, seconds: int) -> None:
        frames = int(seconds * self.sample_rate)
        recording = sd.rec(frames, samplerate=self.sample_rate, channels=1, dtype="int16")
        sd.wait()
        data = np.asarray(recording).reshape(-1)
        with wave.open(str(path), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(self.sample_rate)
            wav.writeframes(data.tobytes())
