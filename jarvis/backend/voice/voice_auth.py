from __future__ import annotations

from pathlib import Path

import numpy as np

from jarvis.backend.core.config import settings


class VoiceAuthenticator:
    """Lightweight voice gate placeholder.

    Production deployments should replace this with a real speaker verification model.
    The interface is intentionally stable so a future ECAPA-TDNN or pyannote verifier can
    drop in without changing wake-word orchestration.
    """

    def __init__(self, profile_path: Path | None = None, threshold: float = 0.78) -> None:
        self.profile_path = profile_path or settings.voice_profile_path
        self.threshold = threshold

    def is_authorized(self, audio_path: Path) -> bool:
        if not settings.voice_auth_enabled:
            return True
        if not self.profile_path.exists():
            return False
        reference = np.load(self.profile_path)
        candidate = self._simple_embedding(audio_path)
        score = float(np.dot(reference, candidate) / (np.linalg.norm(reference) * np.linalg.norm(candidate)))
        return score >= self.threshold

    def enroll(self, audio_path: Path) -> None:
        self.profile_path.parent.mkdir(parents=True, exist_ok=True)
        np.save(self.profile_path, self._simple_embedding(audio_path))

    def _simple_embedding(self, audio_path: Path) -> np.ndarray:
        data = np.frombuffer(audio_path.read_bytes(), dtype=np.uint8).astype(np.float32)
        if data.size == 0:
            return np.ones(32, dtype=np.float32)
        chunks = np.array_split(data, 32)
        vector = np.array([chunk.mean() if chunk.size else 0 for chunk in chunks], dtype=np.float32)
        return vector + 1e-6

