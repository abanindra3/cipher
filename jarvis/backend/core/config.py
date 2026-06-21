from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "JARVIS"
    app_host: str = "127.0.0.1"
    app_port: int = 8765
    database_url: str = "sqlite:///./jarvis.db"
    log_level: str = "INFO"

    openai_api_key: str | None = None
    openai_reasoning_model: str = "gpt-5.5"
    openai_transcribe_model: str = "gpt-4o-transcribe"
    openai_tts_model: str = "gpt-4o-mini-tts"
    openai_tts_voice: str = "coral"

    wake_word: str = "Cipher"
    wake_word_engine: str = Field(default="text", pattern="^(text|porcupine)$")
    voice_auth_enabled: bool = False
    voice_profile_path: Path = Path("./data/voiceprint.npy")

    openweather_api_key: str | None = None
    news_rss_url: str = "https://www.thehindu.com/news/national/feeder/default.rss"
    jobs_rss_url: str = "https://remoteok.com/remote-python-jobs.rss"

    @property
    def sqlite_path(self) -> Path:
        if self.database_url.startswith("sqlite:///"):
            return Path(self.database_url.replace("sqlite:///", "", 1)).resolve()
        return Path("jarvis.db").resolve()


settings = Settings()

