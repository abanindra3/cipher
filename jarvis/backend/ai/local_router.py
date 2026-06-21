from __future__ import annotations

import re
from typing import Any

from jarvis.backend.tools.registry import ToolRegistry


class LocalCommandRouter:
    def __init__(self, tools: ToolRegistry) -> None:
        self.tools = tools

    def try_handle(self, text: str) -> tuple[str, list[dict[str, Any]]] | None:
        cleaned = " ".join(text.strip().split())
        lowered = cleaned.lower()
        tool_results: list[dict[str, Any]] = []

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
        if youtube_query:
            args = {"query": youtube_query}
            result = self.tools.run("open_youtube", args)
            tool_results.append({"name": "open_youtube", "arguments": args, "result": result})
            return self._message(result), tool_results

        facetime_target = self._match_call(cleaned)
        if facetime_target:
            args = {"target": facetime_target}
            result = self.tools.run("facetime_call", args)
            tool_results.append({"name": "facetime_call", "arguments": args, "result": result})
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

        return None

    @staticmethod
    def _after_prefix(lowered: str, original: str, prefixes: list[str]) -> str:
        for prefix in prefixes:
            if lowered.startswith(prefix):
                return original[len(prefix) :].strip()
        return ""

    @staticmethod
    def _match_call(text: str) -> str:
        match = re.search(r"\b(?:call|facetime)\s+(.+?)(?:\s+on\s+facetime)?$", text, re.I)
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
    def _message(result: dict[str, Any]) -> str:
        return str(result.get("message") or result.get("error") or "Done.")
