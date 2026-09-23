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
    session_ttl_minutes: int = Field(default=60, ge=1, le=43200)
    session_cookie_name: str = Field(default="taskforge_session", min_length=1)
    csrf_header_name: str = Field(default="X-CSRF-Token", min_length=1)
    session_cookie_secure: bool = False
    redis_url: str = "redis://127.0.0.1:6379/0"
    redis_timeout_seconds: float = Field(default=0.2, gt=0, le=5)
    project_summary_cache_ttl_seconds: int = Field(default=30, ge=1, le=3600)
    max_request_body_bytes: int = Field(default=1_000_000, ge=1)
    export_storage_dir: str = Field(default=".dist/exports", min_length=1)
    job_lease_seconds: int = Field(default=30, ge=1, le=3600)
    worker_concurrency: int = Field(default=2, ge=1, le=32)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="TASKFORGE_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
