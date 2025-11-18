# app/config.py
import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "FlowMind Core API"
    APP_VERSION: str = "1.0.0"

    # ===========================
    # Database (SQLite)
    # ===========================
    DATABASE_URL: str = "sqlite:///./data/flowmind.db"

    # ===========================
    # RESEND Email Settings
    # ===========================
    RESEND_API_KEY: str | None = os.getenv("RESEND_API_KEY")
    RESEND_FROM_EMAIL: str = os.getenv("RESEND_FROM_EMAIL", "onboarding@resend.dev")

    @property
    def EMAIL_ENABLED(self) -> bool:
        """
        Email gönderimi aktif mi?
        """
        return bool(self.RESEND_API_KEY)

    # .env desteği açık kalsın (lokalde istersen kolay olur)
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
