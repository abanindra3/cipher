from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from jarvis.backend.ai.gemini_client import (
    GeminiClient,
    GeminiRateLimitError,
    extract_function_calls,
    extract_text,
    first_model_content,
)
from jarvis.backend.ai.local_router import LocalCommandRouter
from jarvis.backend.ai.memory_extractor import MemoryExtractor
from jarvis.backend.ai.prompts import SYSTEM_PROMPT, memory_context
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
        self.local_router = LocalCommandRouter(self.tools)
        self.extractor = MemoryExtractor(self.memories)
        self.client = GeminiClient()

    def respond(self, text: str, conversation_id: int | None = None) -> AssistantResult:
        conversation_id = self.conversations.ensure(conversation_id)
        remembered = self.extractor.extract(text)
        self.conversations.add_message(conversation_id, "user", text)

        local = self.local_router.try_handle(text)
        if local:
            reply, tool_results = local
            self.conversations.add_message(conversation_id, "assistant", reply, {"tool_results": tool_results, "local": True})
            return AssistantResult(conversation_id, reply, tool_results, remembered)

        if not self.client.enabled:
            reply, tool_results = self._offline_response(text)
            self.conversations.add_message(conversation_id, "assistant", reply)
            return AssistantResult(conversation_id, reply, tool_results, remembered)

        history = self.conversations.history(conversation_id)
        contents = self._gemini_contents(history)
        system_text = f"{SYSTEM_PROMPT}\n\n{memory_context(self.memories.all())}"

        tool_results: list[dict[str, Any]] = []
        try:
            response = self.client.generate(
                contents=contents,
                function_declarations=self.tools.gemini_function_declarations(),
                system_text=system_text,
            )
        except GeminiRateLimitError:
            reply, tool_results = self._offline_response(text)
            reply = f" limited  {reply}"
            self.conversations.add_message(conversation_id, "assistant", reply, {"tool_results": tool_results})
            return AssistantResult(conversation_id, reply, tool_results, remembered)

        for _ in range(4):
            calls = extract_function_calls(response)
            if not calls:
                break
            model_content = first_model_content(response)
            if model_content:
                contents.append(model_content)
            for call in calls:
                name = call.get("name", "")
                args = call.get("args") or {}
                result = self.tools.run(name, args)
                tool_results.append({"name": name, "arguments": args, "result": result})
                function_response = {
                    "name": name,
                    "response": {"result": result},
                }
                if call.get("id"):
                    function_response["id"] = call["id"]
                contents.append(
                    {
                        "role": "user",
                        "parts": [{"functionResponse": function_response}],
                    }
                )
            try:
                response = self.client.generate(
                    contents=contents,
                    function_declarations=self.tools.gemini_function_declarations(),
                    system_text=system_text,
                )
            except GeminiRateLimitError:
                reply = "I completed the local action. Gemini is rate limited, so I cannot add a detailed explanation right now."
                self.conversations.add_message(conversation_id, "assistant", reply, {"tool_results": tool_results})
                return AssistantResult(conversation_id, reply, tool_results, remembered)

        reply = extract_text(response) or "I completed the request."
        self.conversations.add_message(conversation_id, "assistant", reply, {"tool_results": tool_results})
        return AssistantResult(conversation_id, reply, tool_results, remembered)

    def _gemini_contents(self, history: list[dict[str, str]]) -> list[dict[str, Any]]:
        contents: list[dict[str, Any]] = []
        for item in history:
            role = item["role"]
            if role == "system":
                continue
            gemini_role = "model" if role == "assistant" else "user"
            contents.append({"role": gemini_role, "parts": [{"text": item["content"]}]})
        return contents

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
            "in local  "
            ".",
            tool_results,
        )
