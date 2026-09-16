from uuid import UUID

from redis.exceptions import RedisError

from taskforge.cache import RedisProjectSummaryCache, project_summary_cache_key
from taskforge.models import ProjectSummaryRead

WORKSPACE_ID = UUID("00000000-0000-4000-8000-000000000101")
PROJECT_ID = UUID("00000000-0000-4000-8000-000000000201")


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}
        self.fail_get = False
        self.fail_set = False
        self.fail_delete = False
        self.set_calls: list[tuple[str, str, int]] = []
        self.delete_calls: list[str] = []

    def get(self, key: str) -> str | None:
        if self.fail_get:
            raise RedisError("get failed")
        return self.values.get(key)

    def set(self, key: str, value: str, ex: int) -> None:
        if self.fail_set:
            raise RedisError("set failed")
        self.set_calls.append((key, value, ex))
        self.values[key] = value

    def delete(self, key: str) -> None:
        if self.fail_delete:
            raise RedisError("delete failed")
        self.delete_calls.append(key)
        self.values.pop(key, None)


def test_project_summary_cache_key_includes_schema_tenant_and_resource() -> None:
    key = project_summary_cache_key(WORKSPACE_ID, PROJECT_ID)

    assert key == (
        f"taskforge:v1:workspace:{WORKSPACE_ID}:project:{PROJECT_ID}:summary"
    )


def test_redis_project_summary_cache_sets_and_reads_summary() -> None:
    redis = FakeRedis()
    cache = RedisProjectSummaryCache(redis, ttl_seconds=30)
    summary = ProjectSummaryRead(
        id=PROJECT_ID,
        workspace_id=WORKSPACE_ID,
        name="Launch plan",
        task_count=2,
    )

    cache.set(summary)
    cached = cache.get(WORKSPACE_ID, PROJECT_ID)

    assert cached == summary
    assert redis.set_calls[0][2] == 30


def test_redis_project_summary_cache_get_failure_returns_miss() -> None:
    redis = FakeRedis()
    redis.fail_get = True
    cache = RedisProjectSummaryCache(redis, ttl_seconds=30)

    assert cache.get(WORKSPACE_ID, PROJECT_ID) is None


def test_redis_project_summary_cache_set_failure_is_ignored() -> None:
    redis = FakeRedis()
    redis.fail_set = True
    cache = RedisProjectSummaryCache(redis, ttl_seconds=30)
    summary = ProjectSummaryRead(
        id=PROJECT_ID,
        workspace_id=WORKSPACE_ID,
        name="Launch plan",
        task_count=2,
    )

    cache.set(summary)


def test_redis_project_summary_cache_delete_failure_is_ignored() -> None:
    redis = FakeRedis()
    redis.fail_delete = True
    cache = RedisProjectSummaryCache(redis, ttl_seconds=30)

    cache.delete_key(cache.key(WORKSPACE_ID, PROJECT_ID))
