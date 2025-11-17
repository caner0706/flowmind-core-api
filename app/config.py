# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "FlowMind Core API"
    APP_VERSION: str = "0.1.0"
    ENV: str = "hf-space"

    # DB dosyamız repo kökünde data/flowmind.db
    DATABASE_URL: str = "sqlite:///./data/flowmind.db"

    # ✅ Mail ayarları (HF Spaces Secret olarak set edeceğiz)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str | None = None  # HF’de secret olarak
    SMTP_PASSWORD: str | None = None  # HF’de secret olarak
    SMTP_FROM_EMAIL: str = "no-reply@flowmind.local"  # Gönderici adı/adresi
    EMAIL_VERIFICATION_EXPIRE_MINUTES: int = 30       # Kod geçerlilik süresi

settings = Settings()
