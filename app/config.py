# app/config.py
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Uygulama bilgileri
    APP_NAME: str = "FlowMind Core API"
    APP_VERSION: str = "1.0.0"

    # ===========================
    # Database (SQLite)
    # ===========================
    # Varsayılan: ./data/flowmind.db
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/flowmind.db")


settings = Settings()
