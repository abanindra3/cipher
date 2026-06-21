from __future__ import annotations

import os
import platform
import subprocess
import webbrowser
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

import psutil

from jarvis.backend.db.repositories import NotificationRepository


WINDOWS_APP_ALIASES = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "google chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "vscode": "code",
    "vs code": "code",
    "visual studio code": "code",
    "spotify": "spotify",
    "notepad": "notepad",
}

MAC_APP_ALIASES = {
    "chrome": "Google Chrome",
    "google chrome": "Google Chrome",
    "safari": "Safari",
    "vscode": "Visual Studio Code",
    "vs code": "Visual Studio Code",
    "visual studio code": "Visual Studio Code",
    "spotify": "Spotify",
}


def _popen(command: list[str] | str) -> None:
    subprocess.Popen(command, shell=isinstance(command, str))  # noqa: S603


def open_app(name: str) -> dict[str, Any]:
    system = platform.system().lower()
    if system == "windows":
        app = WINDOWS_APP_ALIASES.get(name.lower(), name)
        _popen(app if isinstance(app, str) else [app])
    elif system == "darwin":
        app = MAC_APP_ALIASES.get(name.lower(), name)
        if name.lower() in MAC_APP_ALIASES and not _mac_app_exists(app):
            return {"error": f"Application not found: {app}"}
        _popen(["open", "-a", app])
    else:
        app = name
        _popen([app])
    return {"message": f"Opening {name}"}


def _mac_app_exists(app: str) -> bool:
    candidates = [
        Path("/Applications") / f"{app}.app",
        Path.home() / "Applications" / f"{app}.app",
    ]
    return any(path.exists() for path in candidates)


def close_app(name: str) -> dict[str, Any]:
    closed: list[str] = []
    needle = name.lower()
    for proc in psutil.process_iter(["pid", "name"]):
        proc_name = (proc.info.get("name") or "").lower()
        if needle in proc_name:
            proc.terminate()
            closed.append(proc_name)
    return {"closed": closed}


def open_website(url: str) -> dict[str, Any]:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    webbrowser.open(url)
    return {"message": f"Opened {url}", "url": url}


def google_search(query: str) -> dict[str, Any]:
    url = f"https://www.google.com/search?q={quote_plus(query)}"
    webbrowser.open(url)
    return {"message": f"Searching Google for {query}", "url": url}


def open_safari(url: str | None = None) -> dict[str, Any]:
    target = url or "https://www.google.com"
    if not target.startswith(("http://", "https://")):
        target = "https://" + target
    if platform.system().lower() == "darwin":
        if not _mac_app_exists("Safari"):
            return {"error": "Safari is not installed or is not in /Applications."}
        _popen(["open", "-a", "Safari", target])
    else:
        webbrowser.open(target)
    return {"message": f"Opened Safari at {target}", "url": target}


def safari_search(query: str) -> dict[str, Any]:
    url = f"https://www.google.com/search?q={quote_plus(query)}"
    return open_safari(url)


def open_youtube(query: str | None = None) -> dict[str, Any]:
    if query:
        url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
    else:
        url = "https://www.youtube.com"
    webbrowser.open(url)
    return {"message": "Opened YouTube", "url": url}


def open_file(path: str) -> dict[str, Any]:
    target = Path(path).expanduser().resolve()
    system = platform.system().lower()
    if system == "windows":
        os.startfile(target)  # type: ignore[attr-defined] # noqa: S606
    elif system == "darwin":
        _popen(["open", str(target)])
    else:
        _popen(["xdg-open", str(target)])
    return {"message": f"Opened {target}", "path": str(target)}


def read_file(path: str, max_chars: int = 6000) -> dict[str, Any]:
    target = Path(path).expanduser().resolve()
    content = target.read_text(encoding="utf-8", errors="replace")[:max_chars]
    return {"path": str(target), "content": content}


def create_folder(path: str) -> dict[str, Any]:
    target = Path(path).expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)
    return {"message": f"Created folder {target}", "path": str(target)}


def create_reminder(text: str, time: str) -> dict[str, Any]:
    NotificationRepository().add("reminder", "Reminder created", f"{text} at {time}")
    return {"message": f"Reminder saved: {text} at {time}"}


def facetime_call(target: str) -> dict[str, Any]:
    url = f"facetime://{quote_plus(target)}"
    webbrowser.open(url)
    return {"message": f"Opening FaceTime call to {target}", "url": url}


def send_sms(target: str, message: str) -> dict[str, Any]:
    separator = "&" if platform.system().lower() == "darwin" else "?"
    url = f"sms:{quote_plus(target)}{separator}body={quote_plus(message)}"
    webbrowser.open(url)
    return {"message": f"Opening Messages to {target}", "url": url}


def open_whatsapp_message(phone: str, message: str) -> dict[str, Any]:
    cleaned = "".join(ch for ch in phone if ch.isdigit())
    if not cleaned:
        return {"error": "A phone number with country code is required for WhatsApp."}
    url = f"https://wa.me/{cleaned}?text={quote_plus(message)}"
    webbrowser.open(url)
    return {"message": f"Opening WhatsApp message to {phone}", "url": url}
