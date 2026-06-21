from __future__ import annotations

import wave
from pathlib import Path

import numpy as np

from jarvis.backend.core.config import settings


class VoiceAuthenticator:
    """Lightweight voice gate placeholder.

    Production deployments should replace this with a real speaker verification model.
    The interface is intentionally stable so a future ECAPA-TDNN or pyannote verifier can
    drop in without changing wake-word orchestration.
    """

    def __init__(self, profile_path: Path | None = None, threshold: float | None = None) -> None:
        self.profile_path = profile_path or settings.voice_profile_path
        self.threshold = threshold if threshold is not None else settings.voice_auth_threshold

    def is_authorized(self, audio_path: Path) -> bool:
        if not settings.voice_auth_enabled:
            return True
        if not self.profile_path.exists():
            print(f"Voice profile missing: {self.profile_path}", flush=True)
            return False
        reference = np.load(self.profile_path)
        candidate = self._simple_embedding(audio_path)
        score = float(np.dot(reference, candidate) / (np.linalg.norm(reference) * np.linalg.norm(candidate)))
        print(f"Voice match score: {score:.2f} / threshold {self.threshold:.2f}", flush=True)
        return score >= self.threshold

    def enroll(self, audio_path: Path) -> None:
        self.profile_path.parent.mkdir(parents=True, exist_ok=True)
        np.save(self.profile_path, self._simple_embedding(audio_path))

    def _simple_embedding(self, audio_path: Path) -> np.ndarray:
        with wave.open(str(audio_path), "rb") as wav:
            frames = wav.readframes(wav.getnframes())
            sample_width = wav.getsampwidth()
        dtype = np.int16 if sample_width == 2 else np.uint8
        audio = np.frombuffer(frames, dtype=dtype).astype(np.float32)
        if audio.size < 512:
            return np.ones(64, dtype=np.float32)

        audio = audio - float(audio.mean())
        max_abs = float(np.max(np.abs(audio))) or 1.0
        audio = audio / max_abs
        chunks = np.array_split(audio, 16)
        features: list[float] = []
        for chunk in chunks:
            if chunk.size < 64:
                continue
            spectrum = np.abs(np.fft.rfft(chunk * np.hanning(chunk.size)))
            bands = np.array_split(spectrum[: min(2048, spectrum.size)], 4)
            features.extend(float(np.log1p(band.mean())) for band in bands)
        vector = np.array(features[:64], dtype=np.float32)
        if vector.size < 64:
            vector = np.pad(vector, (0, 64 - vector.size), constant_values=0.0)
        norm = float(np.linalg.norm(vector)) or 1.0
        return vector / norm
