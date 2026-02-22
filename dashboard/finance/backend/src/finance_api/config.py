from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/finance.db", alias="DATABASE_URL"
    )

    # Gmail OAuth2 — credentials.json and token.json stored in /app/data/
    gmail_credentials_path: str = Field(default="./data/credentials.json", alias="GMAIL_CREDENTIALS_PATH")
    gmail_token_path: str = Field(default="./data/token.json", alias="GMAIL_TOKEN_PATH")

    # Telegram bot
    telegram_bot_token: Optional[str] = Field(default=None, alias="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: Optional[str] = Field(default=None, alias="TELEGRAM_CHAT_ID")
    telegram_high_value_threshold: float = Field(default=5000.0, alias="TELEGRAM_HIGH_VALUE_THRESHOLD")

    # Scheduler
    scheduler_enabled: bool = Field(default=True, alias="SCHEDULER_ENABLED")
    poll_interval_seconds: int = Field(default=120, alias="POLL_INTERVAL_SECONDS")


@lru_cache()
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
