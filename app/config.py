# app/config.py
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "FlowMind Core API"
    APP_VERSION: str = "1.0.0"

    # ===========================
    # Database (SQLite)
    # ===========================
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./flowmind.db")

    # ===========================
    # SMTP / Email settings
    # ===========================
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))

    SMTP_USERNAME: str | None = os.getenv("SMTP_USERNAME", None)  # Gmail adresi
    SMTP_PASSWORD: str | None = os.getenv("SMTP_PASSWORD", None)  # App Password

    # From email gönderici (boş bırakılırsa SMTP_USERNAME kullanılır)
    SMTP_FROM_EMAIL: str | None = os.getenv("SMTP_FROM_EMAIL", None)

    # SMTP aktif mi? env yoksa otomatik False olur
    @property
    def SMTP_ENABLED(self) -> bool:
        return bool(self.SMTP_USERNAME and self.SMTP_PASSWORD)

    class Config:
        env_file = ".env"


settings = Settings()
