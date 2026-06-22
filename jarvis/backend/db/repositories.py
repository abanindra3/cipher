from __future__ import annotations

from datetime import datetime
from typing import Any

from jarvis.backend.db.database import Database, as_json, db


class MemoryRepository:
    def __init__(self, database: Database = db) -> None:
        self.db = database

    def all(self) -> list[dict[str, Any]]:
        return self.db.query("SELECT * FROM memories ORDER BY key")

    def upsert(self, key: str, value: str, source: str = "user", confidence: float = 1.0) -> None:
        self.db.execute(
            """
            INSERT INTO memories(key, value, source, confidence)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
              value = excluded.value,
              source = excluded.source,
              confidence = excluded.confidence,
              updated_at = CURRENT_TIMESTAMP
            """,
            (key, value, source, confidence),
        )

    def delete(self, key: str) -> None:
        self.db.execute("DELETE FROM memories WHERE key = ?", (key,))


class ConversationRepository:
    def __init__(self, database: Database = db) -> None:
        self.db = database

    def ensure(self, conversation_id: int | None = None) -> int:
        if conversation_id:
            rows = self.db.query("SELECT id FROM conversations WHERE id = ?", (conversation_id,))
            if rows:
                return conversation_id
        return self.db.execute("INSERT INTO conversations DEFAULT VALUES")

    def add_message(
        self, conversation_id: int, role: str, content: str, metadata: dict[str, Any] | None = None
    ) -> None:
        self.db.execute(
            "INSERT INTO messages(conversation_id, role, content, metadata_json) VALUES (?, ?, ?, ?)",
            (conversation_id, role, content, as_json(metadata or {})),
        )
        self.db.execute(
            "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (conversation_id,),
        )

    def history(self, conversation_id: int, limit: int = 24) -> list[dict[str, str]]:
        rows = self.db.query(
            """
            SELECT role, content FROM messages
            WHERE conversation_id = ?
            ORDER BY id DESC LIMIT ?
            """,
            (conversation_id, limit),
        )
        return [{"role": row["role"], "content": row["content"]} for row in reversed(rows)]


class ToolLogRepository:
    def __init__(self, database: Database = db) -> None:
        self.db = database

    def add(self, name: str, args: dict[str, Any], result: dict[str, Any], status: str) -> None:
        self.db.execute(
            """
            INSERT INTO tool_logs(name, arguments_json, result_json, status)
            VALUES (?, ?, ?, ?)
            """,
            (name, as_json(args), as_json(result), status),
        )

    def recent(self, limit: int = 100) -> list[dict[str, Any]]:
        return self.db.query("SELECT * FROM tool_logs ORDER BY id DESC LIMIT ?", (limit,))


class NotificationRepository:
    def __init__(self, database: Database = db) -> None:
        self.db = database

    def add(self, channel: str, title: str, body: str) -> int:
        return self.db.execute(
            "INSERT INTO notifications(channel, title, body) VALUES (?, ?, ?)",
            (channel, title, body),
        )

    def list(self, limit: int = 100) -> list[dict[str, Any]]:
        return self.db.query("SELECT * FROM notifications ORDER BY id DESC LIMIT ?", (limit,))

    def add_reminder(self, text: str, due_at: datetime) -> int:
        return self.db.execute(
            "INSERT INTO reminders(text, due_at) VALUES (?, ?)",
            (text, due_at.isoformat()),
        )

    def due_reminders(self, now: datetime) -> list[dict[str, Any]]:
        return self.db.query(
            "SELECT * FROM reminders WHERE delivered = 0 AND due_at <= ? ORDER BY due_at",
            (now.isoformat(),),
        )

    def mark_reminder_delivered(self, reminder_id: int) -> None:
        self.db.execute("UPDATE reminders SET delivered = 1 WHERE id = ?", (reminder_id,))
