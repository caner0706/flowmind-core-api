# app/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "FlowMind Core API"
    APP_VERSION: str = "0.1.0"
    ENV: str = "hf-space"

    # HF Spaces üzerinde kalıcı SQLite dosyası
    # /data klasörü, Spaces'in persistent storage alanı
    DATABASE_URL: str = "sqlite:////data/flowmind.db"

    class Config:
        env_file = ".env"


settings = Settings()
