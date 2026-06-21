from jarvis.backend.ai.client import AssistantEngine
from jarvis.backend.ai.gemini_client import GeminiRateLimitError
from jarvis.backend.tools import build_registry


def test_gemini_tool_declarations_are_exposed():
    declarations = build_registry().gemini_function_declarations()
    names = {item["name"] for item in declarations}

    assert "open_app" in names
    assert "google_search" in names
    assert "fetch_weather" in names
    assert "open_safari" in names
    assert "open_whatsapp_message" in names
    assert all("parameters" in item for item in declarations)


def test_assistant_fallback_mentions_gemini_when_key_missing(monkeypatch, tmp_path):
    monkeypatch.setattr("jarvis.backend.ai.gemini_client.settings.gemini_api_key", None)
    engine = AssistantEngine()
    result = engine.respond("hello")

    assert "GEMINI_API_KEY" in result.text


def test_local_command_bypasses_gemini(monkeypatch):
    def fail_generate(*args, **kwargs):
        raise AssertionError("Gemini should not be called for local commands")

    monkeypatch.setattr("jarvis.backend.ai.gemini_client.settings.gemini_api_key", "test-key")
    monkeypatch.setattr("jarvis.backend.ai.gemini_client.GeminiClient.generate", fail_generate)
    monkeypatch.setattr("jarvis.backend.tools.system_tools._popen", lambda _command: None)
    monkeypatch.setattr("jarvis.backend.tools.system_tools._mac_app_exists", lambda _app: True)

    result = AssistantEngine().respond("open Safari")

    assert result.tool_results[0]["name"] == "open_safari"


def test_rate_limit_does_not_crash(monkeypatch):
    def rate_limited(*args, **kwargs):
        raise GeminiRateLimitError("limited")

    monkeypatch.setattr("jarvis.backend.ai.gemini_client.settings.gemini_api_key", "test-key")
    monkeypatch.setattr("jarvis.backend.ai.gemini_client.GeminiClient.generate", rate_limited)

    result = AssistantEngine().respond("tell me something interesting")

    assert "rate limited" in result.text.lower()
