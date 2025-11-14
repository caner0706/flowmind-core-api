from pydantic_settings import BaseSettings  # ✅ artık buradan

class Settings(BaseSettings):
    APP_NAME: str = "FlowMind Core API"
    APP_VERSION: str = "0.1.0"
    ENV: str = "hf-space"

    # DB dosyamız repo kökünde data/flowmind.db olsun
    DATABASE_URL: str = "sqlite:///./data/flowmind.db"


settings = Settings()
