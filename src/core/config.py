import os
from functools import cache

from pydantic_settings import BaseSettings, SettingsConfigDict

DOTENV_PATH = os.getenv("DOTENV_PATH", ".env")


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=DOTENV_PATH, case_sensitive=True, extra="ignore")

    APP_NAME: str = "Ghosty"
    BUILD_VERSION: str = "0.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "local"

    # Database URLs (required)
    DATABASE_URL: str
    DATABASE_URL_SYNC: str

    def is_production(self) -> bool:
        """Check if the application is running in production environment.

        Returns True only when ENVIRONMENT is set to 'prd' to match k8s cluster naming.
        """
        return self.ENVIRONMENT.lower() == "prd"


@cache
def get_settings() -> Settings:
    """
    Cache settings to avoid reading .env file on every request.
    Use @cache for singleton pattern.
    """
    return Settings()  # type: ignore


settings = get_settings()
