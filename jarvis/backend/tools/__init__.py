from __future__ import annotations

from jarvis.backend.tools.internet_tools import (
    fetch_stock,
    fetch_weather,
    latest_news,
    read_rss,
    search_web,
    sports_scores,
)
from jarvis.backend.tools.registry import ToolDefinition, ToolRegistry
from jarvis.backend.tools.system_tools import (
    close_app,
    create_folder,
    create_reminder,
    google_search,
    open_app,
    open_file,
    open_website,
    open_youtube,
    read_file,
)


def build_registry() -> ToolRegistry:
    registry = ToolRegistry()
    string = {"type": "string"}

    definitions = [
        ToolDefinition("open_app", "Open a desktop application by friendly name.", {"type": "object", "properties": {"name": string}, "required": ["name"]}, open_app),
        ToolDefinition("close_app", "Close a running desktop application after confirmation.", {"type": "object", "properties": {"name": string}, "required": ["name"]}, close_app),
        ToolDefinition("open_website", "Open a website URL in the default browser.", {"type": "object", "properties": {"url": string}, "required": ["url"]}, open_website),
        ToolDefinition("google_search", "Open Google search results for a query.", {"type": "object", "properties": {"query": string}, "required": ["query"]}, google_search),
        ToolDefinition("open_youtube", "Open YouTube, optionally searching for a query.", {"type": "object", "properties": {"query": string}}, open_youtube),
        ToolDefinition("open_file", "Open an existing local file.", {"type": "object", "properties": {"path": string}, "required": ["path"]}, open_file),
        ToolDefinition("read_file", "Read text from an existing local file.", {"type": "object", "properties": {"path": string, "max_chars": {"type": "integer", "default": 6000}}, "required": ["path"]}, read_file),
        ToolDefinition("create_folder", "Create a folder on disk.", {"type": "object", "properties": {"path": string}, "required": ["path"]}, create_folder),
        ToolDefinition("create_reminder", "Create a reminder notification.", {"type": "object", "properties": {"text": string, "time": string}, "required": ["text", "time"]}, create_reminder),
        ToolDefinition("search_web", "Return a live web search URL.", {"type": "object", "properties": {"query": string}, "required": ["query"]}, search_web),
        ToolDefinition("fetch_weather", "Fetch current weather for a location.", {"type": "object", "properties": {"location": string}}, fetch_weather),
        ToolDefinition("fetch_stock", "Fetch a stock price by symbol.", {"type": "object", "properties": {"symbol": string}, "required": ["symbol"]}, fetch_stock),
        ToolDefinition("sports_scores", "Find live sports scores.", {"type": "object", "properties": {"query": string}}, sports_scores),
        ToolDefinition("read_rss", "Read an RSS feed.", {"type": "object", "properties": {"url": string, "limit": {"type": "integer", "default": 5}}}, read_rss),
        ToolDefinition("latest_news", "Fetch latest news from the configured RSS feed.", {"type": "object", "properties": {"topic": string, "limit": {"type": "integer", "default": 5}}}, latest_news),
    ]
    for definition in definitions:
        registry.register(definition)
    return registry

