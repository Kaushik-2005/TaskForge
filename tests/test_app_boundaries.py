import json
import logging

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from taskforge.config import Settings, get_settings
from taskforge.main import create_app


def test_invalid_environment_prevents_startup(monkeypatch: pytest.MonkeyPatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("TASKFORGE_ENVIRONMENT", "broken")

    with pytest.raises(ValidationError):
        create_app()

    get_settings.cache_clear()


def test_request_id_header_is_generated() -> None:
    client = TestClient(
        create_app(Settings(environment="test", storage_backend="memory"))
    )

    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.headers["x-request-id"]


def test_request_id_header_is_preserved() -> None:
    client = TestClient(
        create_app(Settings(environment="test", storage_backend="memory"))
    )

    response = client.get("/health/live", headers={"X-Request-ID": "req-123"})

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "req-123"


def test_access_log_is_structured_and_omits_body(
    caplog: pytest.LogCaptureFixture,
) -> None:
    client = TestClient(
        create_app(Settings(environment="test", storage_backend="memory"))
    )

    with caplog.at_level(logging.INFO, logger="taskforge.api"):
        response = client.post(
            "/api/v1/projects",
            json={"name": "Launch plan"},
            headers={"X-Request-ID": "req-456"},
        )

    assert response.status_code == 201
    record = next(
        json.loads(item.message)
        for item in caplog.records
        if '"event":"http_request"' in item.message
    )
    assert record["request_id"] == "req-456"
    assert record["method"] == "POST"
    assert record["path"] == "/api/v1/projects"
    assert record["status_code"] == 201
    assert "Launch plan" not in caplog.text
