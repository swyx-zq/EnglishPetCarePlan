from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded only from the server environment."""

    app_name: str = "English Pet Care Plan API"
    environment: Literal["development", "test", "production"] = "development"
    api_v1_prefix: str = "/api/v1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="ENGLISH_PET_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
