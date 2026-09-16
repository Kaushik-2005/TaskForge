from dataclasses import dataclass
from typing import Any, Protocol

from redis.exceptions import RedisError

_RATE_LIMIT_SCRIPT = """
local count = redis.call("INCR", KEYS[1])
if count == 1 then
    redis.call("EXPIRE", KEYS[1], ARGV[1])
end
local ttl = redis.call("TTL", KEYS[1])
return {count, ttl}
"""


@dataclass(frozen=True)
class RateLimitResult:
    allowed: bool
    retry_after_seconds: int | None = None


class RedisRateLimitClient(Protocol):
    def eval(self, script: str, numkeys: int, *keys_and_args: object) -> Any: ...


class RateLimiter(Protocol):
    def check(
        self,
        key: str,
        *,
        max_requests: int,
        window_seconds: int,
        fail_open: bool,
    ) -> RateLimitResult: ...


class NullRateLimiter:
    def check(
        self,
        key: str,
        *,
        max_requests: int,
        window_seconds: int,
        fail_open: bool,
    ) -> RateLimitResult:
        return RateLimitResult(allowed=True)


class RedisRateLimiter:
    def __init__(self, redis: RedisRateLimitClient) -> None:
        self.redis = redis

    def check(
        self,
        key: str,
        *,
        max_requests: int,
        window_seconds: int,
        fail_open: bool,
    ) -> RateLimitResult:
        try:
            result = self.redis.eval(_RATE_LIMIT_SCRIPT, 1, key, window_seconds)
            count = int(result[0])

            if count > max_requests:
                ttl = int(result[1])
                retry_after = ttl if ttl > 0 else window_seconds
                return RateLimitResult(
                    allowed=False,
                    retry_after_seconds=retry_after,
                )

            return RateLimitResult(allowed=True)
        except RedisError:
            return RateLimitResult(allowed=fail_open)
