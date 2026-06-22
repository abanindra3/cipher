from __future__ import annotations

import re

from jarvis.backend.db.repositories import MemoryRepository


class MemoryExtractor:
    patterns = [
        (re.compile(r"\bmy name is\s+([a-zA-Z .-]+?)(?:\s+and\b|,|\.|$)", re.I), "name"),
        (re.compile(r"\b(?:i am|i'm)\s+(?:based in|from|living in)\s+([a-zA-Z .-]+?)(?:\s+and\b|,|\.|$)", re.I), "location"),
        (re.compile(r"\b(?:i am|i'm)\s+preparing\s+for\s+([a-zA-Z0-9 .-]+?)(?:\s+and\b|,|\.|$)", re.I), "exam_goal"),
        (re.compile(r"\b(?:i want|i aim|my goal is)\s+(?:to become|to be|become)\s+an?\s+([a-zA-Z .-]+?)(?:\s+and\b|,|\.|$)", re.I), "career_goal"),
        (re.compile(r"\b(?:i am|i'm)\s+applying\s+for\s+([a-zA-Z .-]+?)(?:\s+and\b|,|\.|$)", re.I), "job_search"),
    ]

    def __init__(self, memories: MemoryRepository | None = None) -> None:
        self.memories = memories or MemoryRepository()

    def extract(self, text: str) -> list[dict[str, str]]:
        stored: list[dict[str, str]] = []
        for pattern, key in self.patterns:
            match = pattern.search(text)
            if not match:
                continue
            value = match.group(1).strip(" .")
            if value:
                self.memories.upsert(key, value, source="conversation", confidence=0.85)
                stored.append({"key": key, "value": value})
        return stored
