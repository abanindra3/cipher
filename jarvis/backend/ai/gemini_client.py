from __future__ import annotations

from typing import Any

import httpx

from jarvis.backend.core.config import settings


class GeminiRateLimitError(RuntimeError):
    pass


class GeminiClient:
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or settings.gemini_api_key
        self.model = model or settings.gemini_model

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def generate(
        self,
        contents: list[dict[str, Any]],
        function_declarations: list[dict[str, Any]],
        system_text: str,
    ) -> dict[str, Any]:
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured.")

        url = f"{settings.gemini_api_base}/models/{self.model}:generateContent"
        payload = {
            "systemInstruction": {"parts": [{"text": system_text}]},
            "contents": contents,
            "tools": [{"functionDeclarations": function_declarations}],
            "generationConfig": {
                "temperature": 0.6,
                "topP": 0.9,
                "maxOutputTokens": 1200,
            },
        }
        response = httpx.post(
            url,
            headers={"x-goog-api-key": self.api_key, "Content-Type": "application/json"},
            json=payload,
            timeout=60,
        )
        if response.status_code == 429:
            raise GeminiRateLimitError("Gemini API quota or rate limit exceeded.")
        response.raise_for_status()
        return response.json()


def extract_text(response: dict[str, Any]) -> str:
    parts = _parts(response)
    chunks = [part.get("text", "") for part in parts if "text" in part]
    return "\n".join(chunk for chunk in chunks if chunk).strip()


def extract_function_calls(response: dict[str, Any]) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []
    for part in _parts(response):
        call = part.get("functionCall")
        if call:
            calls.append(call)
    return calls


def first_model_content(response: dict[str, Any]) -> dict[str, Any] | None:
    candidates = response.get("candidates") or []
    if not candidates:
        return None
    return candidates[0].get("content")


def _parts(response: dict[str, Any]) -> list[dict[str, Any]]:
    content = first_model_content(response) or {}
    return content.get("parts") or []
