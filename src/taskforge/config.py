from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TaskForge"
    environment: str = Field(default="local", min_length=1)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="TASKFORGE_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
