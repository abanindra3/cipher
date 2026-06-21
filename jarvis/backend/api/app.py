from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from jarvis.backend.ai import AssistantEngine
from jarvis.backend.api.models import (
    ChatRequest,
    ChatResponse,
    MemoryUpsert,
    NotificationRequest,
    ReminderRequest,
    ToolRequest,
)
from jarvis.backend.core.config import settings
from jarvis.backend.db.repositories import MemoryRepository, NotificationRepository, ToolLogRepository
from jarvis.backend.services.briefing import BriefingService
from jarvis.backend.services.notifications import NotificationService
from jarvis.backend.tools import build_registry


def create_app() -> FastAPI:
    app = FastAPI(
        title="JARVIS API",
        version="0.1.0",
        description="Local REST API for desktop and future Android integrations.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost", "http://127.0.0.1", "*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    memories = MemoryRepository()
    tools = build_registry()
    engine = AssistantEngine(memories=memories, tools=tools)
    notifications = NotificationService()

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok", "name": settings.app_name}

    @app.post("/chat", response_model=ChatResponse)
    def chat(request: ChatRequest) -> ChatResponse:
        result = engine.respond(request.message, request.conversation_id)
        return ChatResponse(
            conversation_id=result.conversation_id,
            response=result.text,
            tool_results=result.tool_results,
            remembered=result.remembered,
        )

    @app.get("/memory")
    def list_memory() -> list[dict]:
        return memories.all()

    @app.post("/memory")
    def upsert_memory(item: MemoryUpsert) -> dict:
        memories.upsert(item.key, item.value, item.source, item.confidence)
        return {"status": "ok"}

    @app.delete("/memory/{key}")
    def delete_memory(key: str) -> dict:
        memories.delete(key)
        return {"status": "ok"}

    @app.get("/tools")
    def list_tools() -> list[dict]:
        return tools.schemas()

    @app.post("/tools/run")
    def run_tool(request: ToolRequest) -> dict:
        return tools.run(request.name, request.arguments, confirmed=request.confirmed)

    @app.get("/tools/logs")
    def tool_logs() -> list[dict]:
        return ToolLogRepository().recent()

    @app.get("/briefing/good-morning")
    def good_morning() -> dict:
        return BriefingService(memories).good_morning()

    @app.post("/notifications")
    def create_notification(request: NotificationRequest) -> dict:
        return notifications.notify(request.channel, request.title, request.body, request.speak)

    @app.get("/notifications")
    def list_notifications() -> list[dict]:
        return NotificationRepository().list()

    @app.post("/reminders")
    def create_reminder(request: ReminderRequest) -> dict:
        return notifications.reminder(request.text, request.due_at)

    @app.post("/android/command")
    def android_command(request: ChatRequest) -> ChatResponse:
        result = engine.respond(request.message, request.conversation_id)
        return ChatResponse(
            conversation_id=result.conversation_id,
            response=result.text,
            tool_results=result.tool_results,
            remembered=result.remembered,
        )

    return app

