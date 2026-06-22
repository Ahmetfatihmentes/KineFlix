from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEFAULT_SECRET_KEY = "kineflix-secret-key-change-in-production"


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    """

    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:password@localhost:5432/kineflix"
    )
    DEBUG: bool = False
    ENVIRONMENT: str = "local"
    TMDB_READ_ACCESS_TOKEN: str | None = None
    TMDB_API_KEY: str | None = None
    SECRET_KEY: str = _DEFAULT_SECRET_KEY
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_TIMEOUT: int = 180
    REDIS_URL: str | None = None
    GROQ_API_KEY: str | None = None
    TFIDF_WEIGHT: float = 0.4
    EMBEDDING_WEIGHT: float = 0.6
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @model_validator(mode="after")
    def _check_secret_key(self) -> "Settings":
        if self.ENVIRONMENT == "production" and self.SECRET_KEY == _DEFAULT_SECRET_KEY:
            raise ValueError(
                "SECRET_KEY must be set to a secure random value in production. "
                "Add SECRET_KEY=<random-string> to your .env file."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
