from typing import Protocol
from uuid import UUID

from redis import Redis
from redis.exceptions import RedisError
from sqlalchemy.orm import Session

from taskforge.models import ProjectSummaryRead

_AFTER_COMMIT_CACHE_DELETES = "after_commit_cache_deletes"


class ProjectSummaryCache(Protocol):
    def key(self, workspace_id: UUID, project_id: UUID) -> str: ...

    def get(
        self, workspace_id: UUID, project_id: UUID
    ) -> ProjectSummaryRead | None: ...

    def set(self, summary: ProjectSummaryRead) -> None: ...

    def delete_key(self, key: str) -> None: ...


class NullProjectSummaryCache:
    def key(self, workspace_id: UUID, project_id: UUID) -> str:
        return project_summary_cache_key(workspace_id, project_id)

    def get(self, workspace_id: UUID, project_id: UUID) -> ProjectSummaryRead | None:
        return None

    def set(self, summary: ProjectSummaryRead) -> None:
        return None

    def delete_key(self, key: str) -> None:
        return None


class RedisProjectSummaryCache:
    def __init__(self, redis: Redis, ttl_seconds: int) -> None:
        self.redis = redis
        self.ttl_seconds = ttl_seconds

    def key(self, workspace_id: UUID, project_id: UUID) -> str:
        return project_summary_cache_key(workspace_id, project_id)

    def get(self, workspace_id: UUID, project_id: UUID) -> ProjectSummaryRead | None:
        try:
            value = self.redis.get(self.key(workspace_id, project_id))
        except RedisError:
            return None

        if value is None:
            return None

        if isinstance(value, bytes):
            value = value.decode("utf-8")

        return ProjectSummaryRead.model_validate_json(value)

    def set(self, summary: ProjectSummaryRead) -> None:
        try:
            self.redis.set(
                self.key(summary.workspace_id, summary.id),
                summary.model_dump_json(),
                ex=self.ttl_seconds,
            )
        except RedisError:
            return None

    def delete_key(self, key: str) -> None:
        try:
            self.redis.delete(key)
        except RedisError:
            return None


def project_summary_cache_key(workspace_id: UUID, project_id: UUID) -> str:
    return f"taskforge:v1:workspace:{workspace_id}:project:{project_id}:summary"


def schedule_after_commit_cache_delete(
    session: Session,
    cache: ProjectSummaryCache,
    key: str,
) -> None:
    deletes = session.info.setdefault(_AFTER_COMMIT_CACHE_DELETES, [])
    deletes.append((cache, key))


def run_after_commit_cache_deletes(session: Session) -> None:
    deletes = session.info.pop(_AFTER_COMMIT_CACHE_DELETES, [])
    for cache, key in deletes:
        cache.delete_key(key)
