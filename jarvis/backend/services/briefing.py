from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from jarvis.backend.db.repositories import MemoryRepository
from jarvis.backend.core.config import settings
from jarvis.backend.tools.internet_tools import fetch_weather, read_rss


class BriefingService:
    def __init__(self, memories: MemoryRepository | None = None) -> None:
        self.memories = memories or MemoryRepository()

    def good_morning(self) -> dict:
        now = datetime.now(ZoneInfo("Asia/Kolkata"))
        location = self._memory("location", "Kolkata")
        weather = self._safe(lambda: fetch_weather(location))
        news = self._safe(lambda: read_rss(limit=5))
        jobs = self._safe(lambda: read_rss(url=settings.jobs_rss_url, limit=3))
        return {
            "date": now.strftime("%A, %d %B %Y"),
            "time": now.strftime("%I:%M %p"),
            "location": location,
            "weather": weather,
            "calendar_events": [],
            "latest_news": news.get("items", []) if isinstance(news, dict) else [],
            "upsc_current_affairs": news.get("items", [])[:3] if isinstance(news, dict) else [],
            "job_updates": jobs.get("items", [])[:3] if isinstance(jobs, dict) else [],
        }

    def _memory(self, key: str, default: str) -> str:
        for item in self.memories.all():
            if item["key"] == key:
                return str(item["value"])
        return default

    @staticmethod
    def _safe(call):
        try:
            return call()
        except Exception as exc:  # noqa: BLE001
            return {"error": str(exc)}
