from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from openai import OpenAI

from jarvis.backend.ai.memory_extractor import MemoryExtractor
from jarvis.backend.ai.prompts import SYSTEM_PROMPT, memory_context
from jarvis.backend.core.config import settings
from jarvis.backend.core.logging import get_logger
from jarvis.backend.db.repositories import ConversationRepository, MemoryRepository
from jarvis.backend.tools import build_registry
from jarvis.backend.tools.registry import ToolRegistry

logger = get_logger(__name__)


@dataclass
class AssistantResult:
    conversation_id: int
    text: str
    tool_results: list[dict[str, Any]]
    remembered: list[dict[str, str]]


class AssistantEngine:
    def __init__(
        self,
        conversations: ConversationRepository | None = None,
        memories: MemoryRepository | None = None,
        tools: ToolRegistry | None = None,
    ) -> None:
        self.conversations = conversations or ConversationRepository()
        self.memories = memories or MemoryRepository()
        self.tools = tools or build_registry()
        self.extractor = MemoryExtractor(self.memories)
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    def respond(self, text: str, conversation_id: int | None = None) -> AssistantResult:
        conversation_id = self.conversations.ensure(conversation_id)
        remembered = self.extractor.extract(text)
        self.conversations.add_message(conversation_id, "user", text)

        if not self.client:
            reply, tool_results = self._offline_response(text)
            self.conversations.add_message(conversation_id, "assistant", reply)
            return AssistantResult(conversation_id, reply, tool_results, remembered)

        history = self.conversations.history(conversation_id)
        input_items: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": memory_context(self.memories.all())},
            *history,
        ]

        tool_results: list[dict[str, Any]] = []
        response = self.client.responses.create(
            model=settings.openai_reasoning_model,
            input=input_items,
            tools=self.tools.schemas(),
        )

        for _ in range(4):
            calls = [item for item in response.output if getattr(item, "type", None) == "function_call"]
            if not calls:
                break
            next_input: list[dict[str, Any]] = []
            for call in calls:
                args = json.loads(call.arguments or "{}")
                result = self.tools.run(call.name, args)
                tool_results.append({"name": call.name, "arguments": args, "result": result})
                next_input.append(
                    {"type": "function_call_output", "call_id": call.call_id, "output": json.dumps(result)}
                )
            response = self.client.responses.create(
                model=settings.openai_reasoning_model,
                input=next_input,
                previous_response_id=response.id,
                tools=self.tools.schemas(),
            )

        reply = getattr(response, "output_text", "") or "I completed the request."
        self.conversations.add_message(conversation_id, "assistant", reply, {"tool_results": tool_results})
        return AssistantResult(conversation_id, reply, tool_results, remembered)

    def _offline_response(self, text: str) -> tuple[str, list[dict[str, Any]]]:
        lowered = text.lower()
        tool_results: list[dict[str, Any]] = []
        simple_routes = [
            ("open chrome", "open_app", {"name": "Chrome"}),
            ("launch chrome", "open_app", {"name": "Chrome"}),
            ("open vs code", "open_app", {"name": "VS Code"}),
            ("launch vs code", "open_app", {"name": "VS Code"}),
            ("open spotify", "open_app", {"name": "Spotify"}),
            ("open youtube", "open_youtube", {}),
        ]
        for phrase, tool_name, args in simple_routes:
            if phrase in lowered:
                result = self.tools.run(tool_name, args)
                tool_results.append({"name": tool_name, "arguments": args, "result": result})
                return result.get("message", "Done."), tool_results

        if lowered.startswith("search "):
            query = text.split(" ", 1)[1]
            result = self.tools.run("google_search", {"query": query})
            tool_results.append({"name": "google_search", "arguments": {"query": query}, "result": result})
            return f"Searching for {query}.", tool_results

        if "good morning jarvis" in lowered:
            result = self.tools.run("latest_news", {"topic": "UPSC current affairs", "limit": 5})
            tool_results.append({"name": "latest_news", "arguments": {"topic": "UPSC current affairs"}, "result": result})
            return "Good morning. I can prepare the full briefing once weather and calendar providers are configured. I fetched the configured news feed.", tool_results

        return (
            "I am running in local fallback mode because OPENAI_API_KEY is not set. "
            "I can still open common apps, search Google, log memories, and expose the REST API.",
            tool_results,
        )

