from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["local", "test", "development", "production"]


class Settings(BaseSettings):
    app_name: str = Field(default="TaskForge", min_length=1)
    environment: Environment = "local"
    log_level: str = Field(
        default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="TASKFORGE_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
