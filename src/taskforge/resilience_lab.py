import threading
from dataclasses import dataclass
from enum import StrEnum


class DependencyStatus(StrEnum):
    success = "success"
    timeout = "timeout"
    too_many_requests = "too_many_requests"
    server_error = "server_error"
    circuit_open = "circuit_open"
    bulkhead_rejected = "bulkhead_rejected"


class BulkheadRejectedError(Exception):
    """Raised when the dependency concurrency limit is full."""


class Bulkhead:
    def __init__(self, max_in_flight: int) -> None:
        if max_in_flight < 1:
            raise ValueError("max_in_flight must be positive")

        self._slots = threading.BoundedSemaphore(max_in_flight)

    def acquire(self) -> None:
        if not self._slots.acquire(blocking=False):
            raise BulkheadRejectedError("dependency concurrency limit reached")

    def release(self) -> None:
        self._slots.release()


RETRYABLE_STATUSES = {
    DependencyStatus.timeout,
    DependencyStatus.too_many_requests,
    DependencyStatus.server_error,
}


class CircuitState(StrEnum):
    closed = "closed"
    open = "open"
    half_open = "half_open"


@dataclass(frozen=True)
class DependencyResponse:
    status: DependencyStatus
    value: str | None = None


class MockDependency:
    def __init__(self, responses: list[DependencyResponse]) -> None:
        if not responses:
            raise ValueError("At least one scripted response is required")
        self.responses = responses
        self.calls = 0
        self.operations: list[str] = []
        self.timeouts: list[float] = []

    def call(self, operation: str, timeout_seconds: float) -> DependencyResponse:
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")

        self.calls += 1
        self.operations.append(operation)
        self.timeouts.append(timeout_seconds)
        response = self.responses[min(self.calls - 1, len(self.responses) - 1)]
        return response


class FakeClock:
    def __init__(self) -> None:
        self.now_seconds = 0.0

    def now(self) -> float:
        return self.now_seconds

    def advance(self, seconds: float) -> None:
        if seconds < 0:
            raise ValueError("seconds must not be negative")
        self.now_seconds += seconds


class CircuitBreaker:
    def __init__(
        self,
        clock: FakeClock,
        failure_threshold: int = 3,
        cooldown_seconds: float = 10.0,
    ) -> None:
        if failure_threshold < 1:
            raise ValueError("failure_threshold must be positive")
        if cooldown_seconds <= 0:
            raise ValueError("cooldown_seconds must be positive")

        self.clock = clock
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self.state = CircuitState.closed
        self.consecutive_failures = 0
        self.opened_at: float | None = None
        self._half_open_probe_in_flight = False

    def allow_call(self) -> bool:
        if self.state == CircuitState.closed:
            return True

        if self.state == CircuitState.open:
            assert self.opened_at is not None
            if self.clock.now() - self.opened_at < self.cooldown_seconds:
                return False
            self.state = CircuitState.half_open
            self._half_open_probe_in_flight = False

        if self.state == CircuitState.half_open:
            if self._half_open_probe_in_flight:
                return False
            self._half_open_probe_in_flight = True
            return True

        return False

    def record_success(self) -> None:
        self.state = CircuitState.closed
        self.consecutive_failures = 0
        self.opened_at = None
        self._half_open_probe_in_flight = False

    def record_failure(self) -> None:
        if self.state == CircuitState.half_open:
            self._open()
            return

        self.consecutive_failures += 1
        if self.consecutive_failures >= self.failure_threshold:
            self._open()

    def _open(self) -> None:
        self.state = CircuitState.open
        self.opened_at = self.clock.now()
        self._half_open_probe_in_flight = False


def call_with_retry(
    dependency: MockDependency,
    operation: str,
    clock: FakeClock,
    deadline_seconds: float,
    max_attempts: int = 3,
    backoff_seconds: float = 1.0,
) -> DependencyResponse:
    if deadline_seconds <= 0:
        raise ValueError("deadline_seconds must be positive")
    if max_attempts < 1:
        raise ValueError("max_attempts must be positive")
    if backoff_seconds < 0:
        raise ValueError("backoff_seconds must not be negative")

    deadline_at = clock.now() + deadline_seconds
    last_response = DependencyResponse(DependencyStatus.timeout)

    for attempt in range(max_attempts):
        remaining = deadline_at - clock.now()
        if remaining <= 0:
            return DependencyResponse(DependencyStatus.timeout)

        last_response = dependency.call(operation, remaining)
        if last_response.status not in RETRYABLE_STATUSES:
            return last_response
        if attempt == max_attempts - 1:
            return last_response

        clock.advance(backoff_seconds)

    return last_response


def call_with_resilience(
    dependency: MockDependency,
    breaker: CircuitBreaker,
    bulkhead: Bulkhead,
    operation: str,
    clock: FakeClock,
    deadline_seconds: float,
    max_attempts: int = 3,
    backoff_seconds: float = 1.0,
) -> DependencyResponse:
    if deadline_seconds <= 0:
        raise ValueError("deadline_seconds must be positive")
    if max_attempts < 1:
        raise ValueError("max_attempts must be positive")
    if backoff_seconds < 0:
        raise ValueError("backoff_seconds must not be negative")

    deadline_at = clock.now() + deadline_seconds
    last_response = DependencyResponse(DependencyStatus.timeout)

    for attempt in range(max_attempts):
        if not breaker.allow_call():
            return DependencyResponse(DependencyStatus.circuit_open)

        try:
            bulkhead.acquire()
        except BulkheadRejectedError:
            return DependencyResponse(DependencyStatus.bulkhead_rejected)

        try:
            remaining = deadline_at - clock.now()
            if remaining <= 0:
                return DependencyResponse(DependencyStatus.timeout)
            last_response = dependency.call(operation, remaining)
        finally:
            bulkhead.release()

        if last_response.status == DependencyStatus.success:
            breaker.record_success()
            return last_response
        if last_response.status not in RETRYABLE_STATUSES:
            return last_response

        breaker.record_failure()
        if attempt == max_attempts - 1:
            return last_response
        clock.advance(backoff_seconds)

    return last_response
