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

    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.5-flash"
    gemini_api_base: str = "https://generativelanguage.googleapis.com/v1beta"
    use_gemini_by_default: bool = False
    user_name: str = "Abanindra"

    wake_word: str = "Cipher"
    wake_word_aliases: str = "cipher,cypher,sipher,sifer,safer,sypher,cifer"
    wake_listen_seconds: int = 5
    wake_debug: bool = True
    wake_word_engine: str = Field(default="text", pattern="^(text|porcupine)$")
    voice_auth_enabled: bool = False
    voice_profile_path: Path = Path("./data/voiceprint.npy")
    voice_auth_threshold: float = 0.55
    voice_reject_message: str = "Voice not authorized. I can only respond to my owner."
    tts_rate: int = 165
    tts_volume: float = 0.95

    openweather_api_key: str | None = None
    news_rss_url: str = "https://www.thehindu.com/news/national/feeder/default.rss"
    jobs_rss_url: str = "https://remoteok.com/remote-python-jobs.rss"

    @property
    def sqlite_path(self) -> Path:
        if self.database_url.startswith("sqlite:///"):
            return Path(self.database_url.replace("sqlite:///", "", 1)).resolve()
        return Path("jarvis.db").resolve()


settings = Settings()
