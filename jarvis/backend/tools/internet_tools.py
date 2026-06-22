from __future__ import annotations

from datetime import UTC, datetime
import re
from html import unescape
from typing import Any
from urllib.parse import quote_plus

import feedparser
import httpx

from jarvis.backend.core.config import settings


def search_web(query: str) -> dict[str, Any]:
    url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
    return {"message": "Open this search URL for live results.", "url": url, "query": query}


def free_web_answer(query: str, limit: int = 5) -> dict[str, Any]:
    url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
    try:
        instant = _duckduckgo_instant(query)
        if instant.get("answer"):
            return instant

        html = httpx.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"}).text
        results = _parse_duckduckgo_html(html, limit)
    except Exception as exc:  # noqa: BLE001 - free web sources should fail as a spoken answer.
        return {
            "query": query,
            "answer": f"I could not reach the free web source right now: {exc}",
            "results": [],
            "url": url,
        }
    if not results:
        return {
            "query": query,
            "answer": "I could not fetch a clean free-web answer right now.",
            "results": [],
            "url": url,
        }
    summary_lines = [f"{idx + 1}. {item['title']}: {item['snippet']}" for idx, item in enumerate(results)]
    return {
        "query": query,
        "answer": "Here is what I found from free web results:\n" + "\n".join(summary_lines),
        "results": results,
        "url": url,
    }


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


def _duckduckgo_instant(query: str) -> dict[str, Any]:
    url = "https://api.duckduckgo.com/"
    data = httpx.get(
        url,
        params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
        timeout=10,
    ).json()
    answer = data.get("AbstractText") or data.get("Answer") or data.get("Definition")
    source = data.get("AbstractSource") or data.get("DefinitionSource") or "DuckDuckGo"
    related = [
        item.get("Text", "")
        for item in data.get("RelatedTopics", [])
        if isinstance(item, dict) and item.get("Text")
    ][:3]
    if not answer and related:
        answer = " ".join(related)
    return {
        "query": query,
        "answer": answer or "",
        "source": source,
        "url": data.get("AbstractURL") or f"https://duckduckgo.com/?q={quote_plus(query)}",
        "results": [],
    }


def _parse_duckduckgo_html(html: str, limit: int) -> list[dict[str, str]]:
    blocks = re.findall(r'<a rel="nofollow" class="result__a" href="(.*?)">(.*?)</a>.*?<a class="result__snippet".*?>(.*?)</a>', html, re.S)
    results: list[dict[str, str]] = []
    for href, title, snippet in blocks[:limit]:
        clean_title = _clean_html(title)
        clean_snippet = _clean_html(snippet)
        if clean_title or clean_snippet:
            results.append({"title": clean_title, "snippet": clean_snippet, "link": unescape(href)})
    return results


def _clean_html(value: str) -> str:
    value = re.sub(r"<.*?>", " ", value)
    return " ".join(unescape(value).split())
