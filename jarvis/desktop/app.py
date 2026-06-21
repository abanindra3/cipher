from __future__ import annotations

import sys
from typing import Any

import httpx
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QPushButton,
    QSystemTrayIcon,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QMenu,
)

from jarvis.backend.core.config import settings


API_BASE = f"http://{settings.app_host}:{settings.app_port}"


class JarvisWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.conversation_id: int | None = None
        self.setWindowTitle("JARVIS")
        self.resize(1100, 760)
        self.setStyleSheet(STYLES)
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self._build_chat()
        self._build_memory()
        self._build_logs()
        self._build_notifications()
        self._build_settings()
        self.refresh_all()

    def _build_chat(self) -> None:
        page = QWidget()
        layout = QVBoxLayout(page)
        header = QLabel("JARVIS")
        header.setObjectName("Title")
        self.chat_log = QTextEdit()
        self.chat_log.setReadOnly(True)
        input_row = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Ask JARVIS or type a command...")
        self.chat_input.returnPressed.connect(self.send_chat)
        send = QPushButton("Send")
        send.clicked.connect(self.send_chat)
        voice = QPushButton("Voice")
        voice.clicked.connect(lambda: self.append_chat("System", "Voice capture runs from the tray listener."))
        input_row.addWidget(self.chat_input)
        input_row.addWidget(send)
        input_row.addWidget(voice)
        layout.addWidget(header)
        layout.addWidget(self.chat_log)
        layout.addLayout(input_row)
        self.tabs.addTab(page, "Chat")

    def _build_memory(self) -> None:
        page = QWidget()
        layout = QVBoxLayout(page)
        self.memory_list = QListWidget()
        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self.refresh_memory)
        layout.addWidget(QLabel("Long-term Memory"))
        layout.addWidget(self.memory_list)
        layout.addWidget(refresh)
        self.tabs.addTab(page, "Memory")

    def _build_logs(self) -> None:
        page = QWidget()
        layout = QVBoxLayout(page)
        self.tool_logs = QTextEdit()
        self.tool_logs.setReadOnly(True)
        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self.refresh_logs)
        layout.addWidget(QLabel("Tool Logs"))
        layout.addWidget(self.tool_logs)
        layout.addWidget(refresh)
        self.tabs.addTab(page, "Tools")

    def _build_notifications(self) -> None:
        page = QWidget()
        layout = QVBoxLayout(page)
        self.notifications = QListWidget()
        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self.refresh_notifications)
        layout.addWidget(QLabel("Notification Center"))
        layout.addWidget(self.notifications)
        layout.addWidget(refresh)
        self.tabs.addTab(page, "Notifications")

    def _build_settings(self) -> None:
        page = QWidget()
        layout = QVBoxLayout(page)
        text = QTextEdit()
        text.setReadOnly(True)
        text.setText(
            "\n".join(
                [
                    f"API: {API_BASE}",
                    f"Wake word: {settings.wake_word}",
                    f"Wake engine: {settings.wake_word_engine}",
                    f"Voice auth enabled: {settings.voice_auth_enabled}",
                    f"Reasoning model: {settings.openai_reasoning_model}",
                    f"Transcription model: {settings.openai_transcribe_model}",
                    f"TTS model: {settings.openai_tts_model}",
                    "",
                    "Edit .env to change settings, then restart JARVIS.",
                ]
            )
        )
        layout.addWidget(QLabel("Settings"))
        layout.addWidget(text)
        self.tabs.addTab(page, "Settings")

    def send_chat(self) -> None:
        message = self.chat_input.text().strip()
        if not message:
            return
        self.chat_input.clear()
        self.append_chat("You", message)
        try:
            payload: dict[str, Any] = {"message": message, "conversation_id": self.conversation_id}
            data = httpx.post(f"{API_BASE}/chat", json=payload, timeout=60).json()
            self.conversation_id = data["conversation_id"]
            self.append_chat("JARVIS", data["response"])
            self.refresh_all()
        except Exception as exc:  # noqa: BLE001
            self.append_chat("System", f"Could not reach API: {exc}")

    def append_chat(self, speaker: str, text: str) -> None:
        self.chat_log.append(f"<b>{speaker}</b>: {text}")

    def refresh_all(self) -> None:
        self.refresh_memory()
        self.refresh_logs()
        self.refresh_notifications()

    def refresh_memory(self) -> None:
        self.memory_list.clear()
        try:
            for item in httpx.get(f"{API_BASE}/memory", timeout=5).json():
                self.memory_list.addItem(f"{item['key']}: {item['value']}")
        except Exception:
            self.memory_list.addItem("API not ready yet.")

    def refresh_logs(self) -> None:
        try:
            logs = httpx.get(f"{API_BASE}/tools/logs", timeout=5).json()
            self.tool_logs.setPlainText("\n\n".join(f"{row['created_at']} {row['name']} {row['status']}\n{row['result_json']}" for row in logs))
        except Exception:
            self.tool_logs.setPlainText("API not ready yet.")

    def refresh_notifications(self) -> None:
        self.notifications.clear()
        try:
            for item in httpx.get(f"{API_BASE}/notifications", timeout=5).json():
                self.notifications.addItem(f"{item['created_at']} [{item['channel']}] {item['title']}: {item['body']}")
        except Exception:
            self.notifications.addItem("API not ready yet.")


def create_tray(app: QApplication, window: JarvisWindow) -> QSystemTrayIcon:
    tray = QSystemTrayIcon(app)
    tray.setToolTip("JARVIS is running")
    menu = QMenu()
    show_action = QAction("Show JARVIS")
    show_action.triggered.connect(window.show)
    hide_action = QAction("Hide")
    hide_action.triggered.connect(window.hide)
    quit_action = QAction("Quit")
    quit_action.triggered.connect(app.quit)
    menu.addAction(show_action)
    menu.addAction(hide_action)
    menu.addSeparator()
    menu.addAction(quit_action)
    tray.setContextMenu(menu)
    tray.show()
    return tray


def run_desktop() -> None:
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = JarvisWindow()
    tray = create_tray(app, window)
    window.show()
    timer = QTimer()
    timer.timeout.connect(lambda: tray.setToolTip("JARVIS is running"))
    timer.start(30_000)
    sys.exit(app.exec())


STYLES = """
QMainWindow, QWidget {
  background: #0f1115;
  color: #eef2f8;
  font-family: Segoe UI, Inter, Arial;
  font-size: 14px;
}
QTabWidget::pane {
  border: 1px solid #2b3140;
}
QTabBar::tab {
  background: #171b24;
  color: #cfd7e6;
  padding: 10px 18px;
  border: 1px solid #2b3140;
}
QTabBar::tab:selected {
  background: #243047;
  color: #ffffff;
}
QTextEdit, QLineEdit, QListWidget {
  background: #151922;
  border: 1px solid #313847;
  border-radius: 6px;
  padding: 10px;
  color: #eef2f8;
}
QPushButton {
  background: #2c7be5;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 10px 16px;
}
QPushButton:hover {
  background: #3d8bfa;
}
QLabel#Title {
  font-size: 28px;
  font-weight: 700;
  color: #f7fafc;
}
"""

