import pytest

from taskforge.resilience_lab import (
    Bulkhead,
    BulkheadRejectedError,
    CircuitBreaker,
    CircuitState,
    DependencyResponse,
    DependencyStatus,
    FakeClock,
    MockDependency,
    call_with_resilience,
    call_with_retry,
)


def test_mock_dependency_replays_scripted_responses() -> None:
    dependency = MockDependency(
        [
            DependencyResponse(DependencyStatus.timeout),
            DependencyResponse(DependencyStatus.success, "ready"),
        ]
    )

    first = dependency.call("health-check", 0.5)
    second = dependency.call("health-check", 0.5)

    assert first.status == DependencyStatus.timeout
    assert second.value == "ready"
    assert dependency.calls == 2
    assert dependency.operations == ["health-check", "health-check"]
    assert dependency.timeouts == [0.5, 0.5]


def test_mock_dependency_rejects_empty_script() -> None:
    with pytest.raises(ValueError, match="scripted response"):
        MockDependency([])


def test_mock_dependency_rejects_non_positive_timeout() -> None:
    dependency = MockDependency([DependencyResponse(DependencyStatus.success)])

    with pytest.raises(ValueError, match="positive"):
        dependency.call("health-check", 0)


def test_circuit_breaker_opens_after_failure_threshold() -> None:
    clock = FakeClock()
    breaker = CircuitBreaker(clock, failure_threshold=3, cooldown_seconds=10)

    assert breaker.allow_call() is True
    breaker.record_failure()
    breaker.record_failure()
    assert breaker.state == CircuitState.closed

    breaker.record_failure()

    assert breaker.state == CircuitState.open
    assert breaker.allow_call() is False


def test_circuit_breaker_allows_one_half_open_probe() -> None:
    clock = FakeClock()
    breaker = CircuitBreaker(clock, failure_threshold=1, cooldown_seconds=10)

    breaker.record_failure()
    assert breaker.state == CircuitState.open
    clock.advance(10)

    assert breaker.allow_call() is True
    assert breaker.state == CircuitState.half_open
    assert breaker.allow_call() is False

    breaker.record_success()
    assert breaker.state == CircuitState.closed
    assert breaker.consecutive_failures == 0


def test_failed_half_open_probe_reopens_circuit() -> None:
    clock = FakeClock()
    breaker = CircuitBreaker(clock, failure_threshold=1, cooldown_seconds=10)

    breaker.record_failure()
    clock.advance(10)
    assert breaker.allow_call() is True

    breaker.record_failure()

    assert breaker.state == CircuitState.open
    assert breaker.allow_call() is False


def test_retry_owner_retries_then_returns_success() -> None:
    dependency = MockDependency(
        [
            DependencyResponse(DependencyStatus.server_error),
            DependencyResponse(DependencyStatus.success, "ready"),
        ]
    )
    clock = FakeClock()

    result = call_with_retry(
        dependency,
        "health-check",
        clock,
        deadline_seconds=5,
        max_attempts=3,
        backoff_seconds=1,
    )

    assert result.value == "ready"
    assert dependency.calls == 2
    assert dependency.timeouts == [5, 4]


def test_retry_owner_stops_at_max_attempts() -> None:
    dependency = MockDependency([DependencyResponse(DependencyStatus.server_error)])
    clock = FakeClock()

    result = call_with_retry(
        dependency,
        "health-check",
        clock,
        deadline_seconds=10,
        max_attempts=3,
        backoff_seconds=1,
    )

    assert result.status == DependencyStatus.server_error
    assert dependency.calls == 3


def test_retry_owner_stops_when_deadline_is_exhausted() -> None:
    dependency = MockDependency([DependencyResponse(DependencyStatus.server_error)])
    clock = FakeClock()

    result = call_with_retry(
        dependency,
        "health-check",
        clock,
        deadline_seconds=1,
        max_attempts=3,
        backoff_seconds=1,
    )

    assert result.status == DependencyStatus.timeout
    assert dependency.calls == 1


def test_retry_owner_does_not_backoff_after_success() -> None:
    dependency = MockDependency([DependencyResponse(DependencyStatus.success, "ready")])
    clock = FakeClock()

    result = call_with_retry(
        dependency,
        "health-check",
        clock,
        deadline_seconds=5,
        max_attempts=3,
        backoff_seconds=1,
    )

    assert result.value == "ready"
    assert dependency.calls == 1
    assert clock.now() == 0


def test_bulkhead_rejects_calls_when_capacity_is_full() -> None:
    bulkhead = Bulkhead(max_in_flight=1)

    bulkhead.acquire()

    with pytest.raises(BulkheadRejectedError, match="concurrency limit"):
        bulkhead.acquire()

    bulkhead.release()
    bulkhead.acquire()
    bulkhead.release()


def test_bulkhead_requires_positive_capacity() -> None:
    with pytest.raises(ValueError, match="positive"):
        Bulkhead(max_in_flight=0)


def test_resilient_call_fails_fast_when_circuit_is_open() -> None:
    dependency = MockDependency([DependencyResponse(DependencyStatus.success)])
    clock = FakeClock()
    breaker = CircuitBreaker(clock, failure_threshold=1, cooldown_seconds=10)
    breaker.record_failure()
    bulkhead = Bulkhead(max_in_flight=1)

    result = call_with_resilience(
        dependency,
        breaker,
        bulkhead,
        "health-check",
        clock,
        deadline_seconds=5,
    )

    assert result.status == DependencyStatus.circuit_open
    assert dependency.calls == 0


def test_resilient_call_fails_fast_when_bulkhead_is_full() -> None:
    dependency = MockDependency([DependencyResponse(DependencyStatus.success)])
    clock = FakeClock()
    breaker = CircuitBreaker(clock)
    bulkhead = Bulkhead(max_in_flight=1)
    bulkhead.acquire()

    try:
        result = call_with_resilience(
            dependency,
            breaker,
            bulkhead,
            "health-check",
            clock,
            deadline_seconds=5,
        )
    finally:
        bulkhead.release()

    assert result.status == DependencyStatus.bulkhead_rejected
    assert dependency.calls == 0


def test_resilient_call_retries_and_closes_circuit_on_success() -> None:
    dependency = MockDependency(
        [
            DependencyResponse(DependencyStatus.server_error),
            DependencyResponse(DependencyStatus.success, "ready"),
        ]
    )
    clock = FakeClock()
    breaker = CircuitBreaker(clock, failure_threshold=3, cooldown_seconds=10)
    bulkhead = Bulkhead(max_in_flight=1)

    result = call_with_resilience(
        dependency,
        breaker,
        bulkhead,
        "health-check",
        clock,
        deadline_seconds=5,
        max_attempts=3,
        backoff_seconds=1,
    )

    assert result.value == "ready"
    assert dependency.calls == 2
    assert breaker.state == CircuitState.closed
    assert dependency.timeouts == [5, 4]


def test_resilient_call_success_resets_previous_failures() -> None:
    dependency = MockDependency([DependencyResponse(DependencyStatus.success, "ready")])
    clock = FakeClock()
    breaker = CircuitBreaker(clock, failure_threshold=3, cooldown_seconds=10)
    breaker.record_failure()
    breaker.record_failure()
    bulkhead = Bulkhead(max_in_flight=1)

    result = call_with_resilience(
        dependency,
        breaker,
        bulkhead,
        "health-check",
        clock,
        deadline_seconds=5,
    )

    assert result.value == "ready"
    assert breaker.state == CircuitState.closed
    assert breaker.consecutive_failures == 0
