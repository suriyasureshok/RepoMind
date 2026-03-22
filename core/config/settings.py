# core/config/settings.py

from pydantic_settings import BaseSettings, SettingsConfigDict

from core.logging import logger


class Settings(BaseSettings):
    # Infra
    REDIS_URL: str = "redis://localhost:6379"

    # Workspace
    WORKSPACE_PATH: str = "./workspace"

    # LLM
    LLM_API_KEY_1: str | None = None
    LLM_API_KEY_2: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Singleton instance
settings = Settings()
logger.info("Settings initialized")
