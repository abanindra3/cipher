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
    engine = AssistantEngine()
    engine.client.api_key = None
    result = engine.respond("ask gemini hello")

    assert "without Gemini" in result.text


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

    monkeypatch.setattr("jarvis.backend.ai.client.settings.use_gemini_by_default", True)
    result = AssistantEngine().respond("ask gemini tell me something interesting")

    assert "rate limited" in result.text.lower()


def test_basic_replies_do_not_need_gemini(monkeypatch):
    monkeypatch.setattr("jarvis.backend.ai.gemini_client.settings.gemini_api_key", "test-key")
    result = AssistantEngine().respond("good evening")
    assert "Good evening" in result.text


def test_name_memory_local_reply():
    result = AssistantEngine().respond("my name is Abanindra")
    assert "Abanindra" in result.text


def test_youtube_query_routes_locally(monkeypatch):
    monkeypatch.setattr("jarvis.backend.tools.system_tools._open_url", lambda _url: None)
    result = AssistantEngine().respond("open laxmikant polity video on youtube")
    assert result.tool_results[0]["name"] == "open_youtube"


def test_reminder_routes_locally():
    result = AssistantEngine().respond("remind me to revise polity in 1 minute")
    assert result.tool_results[0]["name"] == "create_reminder"
