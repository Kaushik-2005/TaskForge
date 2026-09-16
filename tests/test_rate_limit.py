import pytest
from redis.exceptions import RedisError

from taskforge.rate_limit import NullRateLimiter, RedisRateLimiter


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, int] = {}
        self.expiries: dict[str, int] = {}
        self.eval_calls: list[tuple[str, int, tuple[object, ...]]] = []

    def eval(self, script: str, numkeys: int, *keys_and_args: object) -> list[int]:
        self.eval_calls.append((script, numkeys, keys_and_args))
        key = str(keys_and_args[0])
        window_seconds = int(keys_and_args[1])
        self.values[key] = self.values.get(key, 0) + 1
        if self.values[key] == 1:
            self.expiries[key] = window_seconds
        return [self.values[key], self.expiries.get(key, -1)]


class FailingRedis:
    def eval(self, script: str, numkeys: int, *keys_and_args: object) -> list[int]:
        raise RedisError("redis unavailable")


def test_null_rate_limiter_allows_requests() -> None:
    limiter = NullRateLimiter()

    result = limiter.check(
        "any-key",
        max_requests=1,
        window_seconds=60,
        fail_open=False,
    )

    assert result.allowed is True
    assert result.retry_after_seconds is None


def test_redis_rate_limiter_allows_requests_under_limit() -> None:
    redis = FakeRedis()
    limiter = RedisRateLimiter(redis)

    first = limiter.check(
        "login:test",
        max_requests=2,
        window_seconds=60,
        fail_open=False,
    )
    second = limiter.check(
        "login:test",
        max_requests=2,
        window_seconds=60,
        fail_open=False,
    )

    assert first.allowed is True
    assert second.allowed is True
    assert redis.values["login:test"] == 2
    assert redis.expiries["login:test"] == 60


def test_redis_rate_limiter_uses_one_atomic_script_per_check() -> None:
    redis = FakeRedis()
    limiter = RedisRateLimiter(redis)

    limiter.check(
        "login:test",
        max_requests=2,
        window_seconds=60,
        fail_open=False,
    )

    assert len(redis.eval_calls) == 1
    _, numkeys, keys_and_args = redis.eval_calls[0]
    assert numkeys == 1
    assert keys_and_args == ("login:test", 60)


def test_redis_rate_limiter_blocks_after_limit() -> None:
    redis = FakeRedis()
    limiter = RedisRateLimiter(redis)

    limiter.check("login:test", max_requests=2, window_seconds=60, fail_open=False)
    limiter.check("login:test", max_requests=2, window_seconds=60, fail_open=False)

    blocked = limiter.check(
        "login:test",
        max_requests=2,
        window_seconds=60,
        fail_open=False,
    )

    assert blocked.allowed is False
    assert blocked.retry_after_seconds == 60


@pytest.mark.parametrize(
    ("fail_open", "expected_allowed"),
    [
        (True, True),
        (False, False),
    ],
)
def test_redis_rate_limiter_outage_policy(
    fail_open: bool,
    expected_allowed: bool,
) -> None:
    limiter = RedisRateLimiter(FailingRedis())

    result = limiter.check(
        "login:test",
        max_requests=2,
        window_seconds=60,
        fail_open=fail_open,
    )

    assert result.allowed is expected_allowed
