from functools import lru_cache
from typing import Literal
from uuid import UUID

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["local", "test", "development", "production"]
StorageBackend = Literal["memory", "postgres"]


class Settings(BaseSettings):
    app_name: str = Field(default="TaskForge", min_length=1)
    environment: Environment = "local"
    log_level: str = Field(
        default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$"
    )
    storage_backend: StorageBackend = "postgres"
    database_url: str = (
        "postgresql+psycopg://taskforge:taskforge_dev_password@127.0.0.1:5433/taskforge"
    )
    database_pool_size: int = Field(default=5, ge=1, le=50)
    database_max_overflow: int = Field(default=0, ge=0, le=50)
    database_pool_timeout_seconds: int = Field(default=5, ge=1, le=60)
    default_workspace_id: UUID = UUID("00000000-0000-4000-8000-000000000101")
    default_workspace_name: str = Field(default="Local workspace", min_length=1)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="TASKFORGE_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
