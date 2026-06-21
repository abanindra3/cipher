from __future__ import annotations

from datetime import datetime

from jarvis.backend.db.repositories import NotificationRepository
from jarvis.backend.voice.tts import TextToSpeech


class NotificationService:
    def __init__(self, repo: NotificationRepository | None = None, tts: TextToSpeech | None = None) -> None:
        self.repo = repo or NotificationRepository()
        self.tts = tts or TextToSpeech()

    def notify(self, channel: str, title: str, body: str, speak: bool = False) -> dict:
        notification_id = self.repo.add(channel, title, body)
        if speak:
            self.tts.speak(f"{title}. {body}")
        return {"id": notification_id, "channel": channel, "title": title, "body": body}

    def reminder(self, text: str, due_at: datetime) -> dict:
        reminder_id = self.repo.add_reminder(text, due_at)
        return {"id": reminder_id, "text": text, "due_at": due_at.isoformat()}

