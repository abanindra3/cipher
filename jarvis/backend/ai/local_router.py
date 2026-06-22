from __future__ import annotations

import re
from typing import Any

from jarvis.backend.core.config import settings
from jarvis.backend.db.repositories import MemoryRepository
from jarvis.backend.tools.registry import ToolRegistry


class LocalCommandRouter:
    def __init__(self, tools: ToolRegistry, memories: MemoryRepository | None = None) -> None:
        self.tools = tools
        self.memories = memories or MemoryRepository()

    def try_handle(self, text: str) -> tuple[str, list[dict[str, Any]]] | None:
        cleaned = " ".join(text.strip().split())
        lowered = cleaned.lower()
        tool_results: list[dict[str, Any]] = []

        basic = self._basic_reply(cleaned)
        if basic:
            return basic, tool_results

        name = self._remember_name(cleaned)
        if name:
            return f"Nice to meet you, {name}. I will remember your name, boss.", tool_results

        routes = [
            (("open safari", "launch safari"), "open_safari", {}),
            (("open chrome", "launch chrome"), "open_app", {"name": "Chrome"}),
            (("open google chrome", "launch google chrome"), "open_app", {"name": "Chrome"}),
            (("open vs code", "launch vs code", "open vscode", "launch vscode"), "open_app", {"name": "VS Code"}),
            (("open spotify", "launch spotify"), "open_app", {"name": "Spotify"}),
            (("open youtube", "launch youtube"), "open_youtube", {}),
        ]
        for phrases, tool_name, args in routes:
            if any(lowered.startswith(phrase) for phrase in phrases):
                result = self.tools.run(tool_name, args)
                tool_results.append({"name": tool_name, "arguments": args, "result": result})
                return self._message(result), tool_results

        open_site = self._after_prefix(lowered, cleaned, ["open website ", "open site ", "open "])
        if open_site and "." in open_site and " " not in open_site:
            args = {"url": open_site}
            result = self.tools.run("open_website", args)
            tool_results.append({"name": "open_website", "arguments": args, "result": result})
            return self._message(result), tool_results

        safari_search = self._after_prefix(lowered, cleaned, ["search in safari ", "safari search "])
        if safari_search:
            args = {"query": safari_search}
            result = self.tools.run("safari_search", args)
            tool_results.append({"name": "safari_search", "arguments": args, "result": result})
            return self._message(result), tool_results

        google_search = self._after_prefix(lowered, cleaned, ["search google for ", "google search ", "search "])
        if google_search:
            args = {"query": google_search}
            result = self.tools.run("google_search", args)
            tool_results.append({"name": "google_search", "arguments": args, "result": result})
            return self._message(result), tool_results

        weather = self._after_prefix(lowered, cleaned, ["weather in ", "what is the weather in "])
        if weather:
            args = {"location": weather}
            result = self.tools.run("fetch_weather", args)
            tool_results.append({"name": "fetch_weather", "arguments": args, "result": result})
            if "error" in result:
                return self._message(result), tool_results
            return f"The weather in {weather} is {result.get('temperature_c')} degrees, {result.get('condition')}.", tool_results

        youtube_query = self._after_prefix(lowered, cleaned, ["youtube search ", "search youtube for "])
        if not youtube_query:
            youtube_query = self._match_youtube_video(cleaned)
        if youtube_query:
            args = {"query": youtube_query}
            result = self.tools.run("open_youtube", args)
            tool_results.append({"name": "open_youtube", "arguments": args, "result": result})
            return self._message(result), tool_results

        facetime_target = self._match_call(cleaned)
        if facetime_target:
            args = {"target": facetime_target}
            result = self.tools.run("phone_call", args)
            tool_results.append({"name": "phone_call", "arguments": args, "result": result})
            return self._message(result), tool_results

        whatsapp = self._match_message(cleaned, platform="whatsapp")
        if whatsapp:
            args = {"phone": whatsapp[0], "message": whatsapp[1]}
            result = self.tools.run("open_whatsapp_message", args)
            tool_results.append({"name": "open_whatsapp_message", "arguments": args, "result": result})
            return self._message(result), tool_results

        sms = self._match_message(cleaned, platform="sms")
        if sms:
            args = {"target": sms[0], "message": sms[1]}
            result = self.tools.run("send_sms", args)
            tool_results.append({"name": "send_sms", "arguments": args, "result": result})
            return self._message(result), tool_results

        reminder = self._match_reminder(cleaned)
        if reminder:
            args = {"text": reminder[0], "time": reminder[1]}
            result = self.tools.run("create_reminder", args)
            tool_results.append({"name": "create_reminder", "arguments": args, "result": result})
            return self._message(result), tool_results

        note = self._match_note(cleaned)
        if note:
            args = {"title": note[0], "body": note[1]}
            result = self.tools.run("add_note", args)
            tool_results.append({"name": "add_note", "arguments": args, "result": result})
            return self._message(result), tool_results

        free_query = self._match_free_answer(cleaned)
        if free_query:
            args = {"query": free_query, "limit": 5}
            result = self.tools.run("free_web_answer", args)
            tool_results.append({"name": "free_web_answer", "arguments": args, "result": result})
            return self._format_web_answer(result), tool_results

        return None

    def _basic_reply(self, text: str) -> str:
        lowered = text.lower().strip(" .!?")
        name = self._user_name()
        if lowered in {"hi", "hello", "hey", "jarvis", "cipher"}:
            return f"Yes boss, I am listening."
        if "good morning" in lowered:
            return f"Good morning, {name}. Ready when you are, boss."
        if "good afternoon" in lowered:
            return f"Good afternoon, {name}. Tell me what to handle."
        if "good evening" in lowered:
            return f"Good evening, {name}. I am online and ready."
        if "good night" in lowered:
            return f"Good night, {name}. I will stay quiet in the background."
        if "how are you" in lowered:
            return "I am running smooth, boss. Voice, tools, reminders, and local search are online."
        if lowered in {"thanks", "thank you", "thank you jarvis"}:
            return "Anytime, boss."
        if "what is my name" in lowered or "do you know my name" in lowered:
            return f"Your name is {name}."
        if "who are you" in lowered:
            return f"I am JARVIS, your local AI assistant. I can listen, speak, open apps, search, take notes, remind you, and help with UPSC/job work."
        if lowered in {"yes boss", "yes jarvis"}:
            return "Yes boss. Standing by."
        return ""

    def _remember_name(self, text: str) -> str:
        match = re.search(r"\bmy name is\s+([a-zA-Z .-]+)", text, re.I)
        if not match:
            return ""
        name = match.group(1).strip(" .")
        self.memories.upsert("name", name, source="conversation", confidence=1.0)
        return name

    @staticmethod
    def _after_prefix(lowered: str, original: str, prefixes: list[str]) -> str:
        for prefix in prefixes:
            if lowered.startswith(prefix):
                return original[len(prefix) :].strip()
        return ""

    @staticmethod
    def _match_call(text: str) -> str:
        match = re.search(r"\b(?:call|phone|dial)\s+(.+?)(?:\s+on\s+(?:phone|sim|facetime))?$", text, re.I)
        return match.group(1).strip() if match else ""

    @staticmethod
    def _match_message(text: str, platform: str) -> tuple[str, str] | None:
        if platform == "whatsapp":
            pattern = r"\b(?:send\s+)?(?:whatsapp|whatsapp message)\s+(?:message\s+)?(?:to\s+)?(.+?)\s+(?:saying|say|message)\s+(.+)$"
        else:
            pattern = r"\b(?:send\s+)?(?:sms|text|message)\s+(?:to\s+)?(.+?)\s+(?:saying|say|message)\s+(.+)$"
        match = re.search(pattern, text, re.I)
        if not match:
            return None
        return match.group(1).strip(), match.group(2).strip()

    @staticmethod
    def _match_youtube_video(text: str) -> str:
        patterns = [
            r"\bopen\s+(.+?)\s+(?:video\s+)?(?:on|in)\s+youtube$",
            r"\bplay\s+(.+?)\s+(?:on|in)\s+youtube$",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.I)
            if match:
                return match.group(1).strip()
        return ""

    @staticmethod
    def _match_reminder(text: str) -> tuple[str, str] | None:
        match = re.search(r"\bremind me to\s+(.+?)\s+(at|in)\s+(.+)$", text, re.I)
        if match:
            return match.group(1).strip(), f"{match.group(2)} {match.group(3).strip()}"
        match = re.search(r"\breminder\s+(.+?)\s+(at|in)\s+(.+)$", text, re.I)
        if match:
            return match.group(1).strip(), f"{match.group(2)} {match.group(3).strip()}"
        return None

    @staticmethod
    def _match_note(text: str) -> tuple[str, str] | None:
        match = re.search(r"\b(?:take|make|add|write)\s+(?:a\s+)?note\s+(?:that\s+)?(.+)$", text, re.I)
        if not match:
            return None
        body = match.group(1).strip()
        title = body[:48].strip() or "JARVIS Note"
        return title, body

    @staticmethod
    def _match_free_answer(text: str) -> str:
        lowered = text.lower()
        prefixes = [
            "tell me about ",
            "tell me ",
            "what is ",
            "who is ",
            "explain ",
            "search online for ",
            "find information about ",
        ]
        for prefix in prefixes:
            if lowered.startswith(prefix):
                return text[len(prefix) :].strip()
        if "upsc" in lowered or "prelims" in lowered or "current affairs" in lowered:
            return text
        return ""

    def _user_name(self) -> str:
        for item in self.memories.all():
            if item["key"] == "name":
                return str(item["value"])
        return settings.user_name

    @staticmethod
    def _format_web_answer(result: dict[str, Any]) -> str:
        if result.get("error"):
            return str(result["error"])
        answer = result.get("answer") or "I could not find a clean answer."
        url = result.get("url")
        if url:
            return f"{answer}\nSource: {url}"
        return str(answer)

    @staticmethod
    def _message(result: dict[str, Any]) -> str:
        return str(result.get("message") or result.get("error") or "Done.")
