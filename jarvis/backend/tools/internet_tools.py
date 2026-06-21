from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from urllib.parse import quote_plus

import feedparser
import httpx

from jarvis.backend.core.config import settings


def search_web(query: str) -> dict[str, Any]:
    url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
    return {"message": "Open this search URL for live results.", "url": url, "query": query}


def fetch_weather(location: str = "Kolkata") -> dict[str, Any]:
    if settings.openweather_api_key:
        params = {"q": location, "appid": settings.openweather_api_key, "units": "metric"}
        data = httpx.get("https://api.openweathermap.org/data/2.5/weather", params=params, timeout=8).json()
        return {
            "location": location,
            "temperature_c": data.get("main", {}).get("temp"),
            "condition": data.get("weather", [{}])[0].get("description"),
        }
    url = f"https://wttr.in/{quote_plus(location)}?format=j1"
    data = httpx.get(url, timeout=8).json()
    current = data["current_condition"][0]
    return {
        "location": location,
        "temperature_c": current.get("temp_C"),
        "condition": current.get("weatherDesc", [{}])[0].get("value"),
    }


def fetch_stock(symbol: str) -> dict[str, Any]:
    url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={quote_plus(symbol)}"
    data = httpx.get(url, timeout=8).json()
    quote = (data.get("quoteResponse", {}).get("result") or [{}])[0]
    return {
        "symbol": symbol.upper(),
        "price": quote.get("regularMarketPrice"),
        "currency": quote.get("currency"),
        "market_state": quote.get("marketState"),
    }


def read_rss(url: str | None = None, limit: int = 5) -> dict[str, Any]:
    feed = feedparser.parse(url or settings.news_rss_url)
    items = [
        {"title": entry.get("title"), "link": entry.get("link"), "summary": entry.get("summary", "")}
        for entry in feed.entries[:limit]
    ]
    return {"feed": feed.feed.get("title", url), "items": items}


def sports_scores(query: str = "India cricket") -> dict[str, Any]:
    return {
        "message": "Sports scores require a configured provider. Search URL returned.",
        "url": f"https://www.google.com/search?q={quote_plus(query + ' live score')}",
    }


def latest_news(topic: str = "India", limit: int = 5) -> dict[str, Any]:
    return read_rss(settings.news_rss_url, limit=limit) | {"topic": topic, "fetched_at": datetime.now(UTC)}

