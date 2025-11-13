from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "FlowMind Core API"
    APP_VERSION: str = "0.1.0"
    ENV: str = "hf-space"  # local, staging, prod vs. ileride ayırabiliriz

    # Şimdilik basit bir SQLite URL; ileride HF persistent storage ile özelleştiririz
    DATABASE_URL: str = "sqlite:///./flowmind.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
