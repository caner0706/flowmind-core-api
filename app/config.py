# app/config.py
import os
from pydantic_settings import BaseSettings  # ✅ DÜZGÜN IMPORT (pydantic değil)


class Settings(BaseSettings):
    APP_NAME: str = "FlowMind Core API"
    APP_VERSION: str = "1.0.0"

    # ===========================
    # Database (SQLite)
    # ===========================
    # Eski path ile uyumlu: ./data/flowmind.db
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/flowmind.db")

    # ===========================
    # SMTP / Email settings
    # ===========================
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))

    # Gmail adresin ve App Password ENV’den geliyor
    SMTP_USERNAME: str | None = os.getenv("SMTP_USERNAME", None)
    SMTP_PASSWORD: str | None = os.getenv("SMTP_PASSWORD", None)

    # Gönderici mail adresi (boşsa SMTP_USERNAME kullanılır)
    SMTP_FROM_EMAIL: str | None = os.getenv("SMTP_FROM_EMAIL", None)

    @property
    def SMTP_ENABLED(self) -> bool:
        """
        SMTP_USERNAME + SMTP_PASSWORD varsa True, yoksa False döner.
        Böylece mail ayarı yoksa sistem patlamıyor, sadece mail atlamış oluyoruz.
        """
        return bool(self.SMTP_USERNAME and self.SMTP_PASSWORD)


settings = Settings()
