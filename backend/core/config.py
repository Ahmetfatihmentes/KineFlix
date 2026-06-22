from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    """

    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:password@localhost:5432/kineflix"
    )
    DEBUG: bool = False
    TMDB_READ_ACCESS_TOKEN: str | None = None
    TMDB_API_KEY: str | None = None
    SECRET_KEY: str = "kineflix-secret-key-change-in-production"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_TIMEOUT: int = 180
    REDIS_URL: str | None = None
    GROQ_API_KEY: str | None = None
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
