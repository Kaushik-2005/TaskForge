from concurrent.futures import ThreadPoolExecutor
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from test_authorization import (
    LoggedInUser,
    create_workspace,
    login_existing_user,
    register_and_login,
)

from taskforge.config import Settings
from taskforge.errors import IdempotencyConflictError
from taskforge.jobs import ExportRepository, export_request_hash
from taskforge.main import create_app


def test_export_request_hash_is_deterministic() -> None:
    workspace_id = UUID("11111111-1111-1111-1111-111111111111")

    assert export_request_hash(workspace_id) == export_request_hash(workspace_id)


def test_export_request_hash_includes_workspace() -> None:
    first_workspace = UUID("11111111-1111-1111-1111-111111111111")
    second_workspace = UUID("22222222-2222-2222-2222-222222222222")

    assert export_request_hash(first_workspace) != export_request_hash(second_workspace)


def test_export_request_hash_is_sha256_hex() -> None:
    workspace_id = UUID("11111111-1111-1111-1111-111111111111")

    result = export_request_hash(workspace_id)

    assert len(result) == 64
    assert all(character in "0123456789abcdef" for character in result)


def make_settings(
    url: str,
    export_storage_dir: str,
    pool_size: int = 2,
) -> Settings:
    return Settings(
        environment="test",
        storage_backend="postgres",
        database_url=url,
        database_pool_size=pool_size,
        database_max_overflow=0,
        database_pool_timeout_seconds=2,
        export_storage_dir=export_storage_dir,
    )


def test_same_key_and_request_replays_existing_export(
    migrated_database_url: str,
    tmp_path,
) -> None:
    app = create_app(make_settings(migrated_database_url, str(tmp_path)))

    with TestClient(app) as client:
        user = register_and_login(client, "idempotency@example.com")
        workspace_id = create_workspace(client, user)
        headers = {
            "X-CSRF-Token": user.csrf_token,
            "Idempotency-Key": "same-export-request",
        }

        first = client.post(
            f"/api/v1/workspaces/{workspace_id}/exports",
            headers=headers,
        )
        second = client.post(
            f"/api/v1/workspaces/{workspace_id}/exports",
            headers=headers,
        )

    assert first.status_code == 202
    assert second.status_code == 202
    assert second.json()["id"] == first.json()["id"]


def test_same_key_in_different_workspaces_is_independent(
    migrated_database_url: str,
    tmp_path,
) -> None:
    app = create_app(make_settings(migrated_database_url, str(tmp_path)))

    with TestClient(app) as client:
        user = register_and_login(client, "idempotency-conflict@example.com")
        first_workspace_id = create_workspace(client, user)
        second_workspace_id = create_workspace(client, user)
        headers = {
            "X-CSRF-Token": user.csrf_token,
            "Idempotency-Key": "reused-key",
        }

        first = client.post(
            f"/api/v1/workspaces/{first_workspace_id}/exports",
            headers=headers,
        )
        second = client.post(
            f"/api/v1/workspaces/{second_workspace_id}/exports",
            headers=headers,
        )

    assert first.status_code == 202
    assert second.status_code == 202
    assert second.json()["id"] != first.json()["id"]


def test_same_scope_key_with_different_hash_returns_conflict(
    migrated_database_url: str,
    tmp_path,
) -> None:
    app = create_app(make_settings(migrated_database_url, str(tmp_path)))

    with TestClient(app) as client:
        user = register_and_login(client, "idempotency-hash-conflict@example.com")
        workspace_id = create_workspace(client, user)
        headers = {
            "X-CSRF-Token": user.csrf_token,
            "Idempotency-Key": "same-scope-key",
        }
        response = client.post(
            f"/api/v1/workspaces/{workspace_id}/exports",
            headers=headers,
        )
        assert response.status_code == 202

    with app.state.session_factory() as session:
        repository = ExportRepository(session)
        with pytest.raises(IdempotencyConflictError):
            repository.create_idempotent_for_user(
                UUID(user.id),
                UUID(workspace_id),
                "same-scope-key",
                "different-request-hash",
            )
        session.rollback()


def test_export_requires_idempotency_key(
    migrated_database_url: str,
    tmp_path,
) -> None:
    app = create_app(make_settings(migrated_database_url, str(tmp_path)))

    with TestClient(app) as client:
        user = register_and_login(client, "idempotency-missing@example.com")
        workspace_id = create_workspace(client, user)

        response = client.post(
            f"/api/v1/workspaces/{workspace_id}/exports",
            headers={"X-CSRF-Token": user.csrf_token},
        )

    assert response.status_code == 422


def test_concurrent_same_key_creates_one_logical_export(
    migrated_database_url: str,
    tmp_path,
) -> None:
    app = create_app(make_settings(migrated_database_url, str(tmp_path), pool_size=6))
    email = "idempotency-concurrent@example.com"
    idempotency_key = "concurrent-key"

    with TestClient(app) as setup_client:
        user = register_and_login(setup_client, email)
        workspace_id = create_workspace(setup_client, user)

    first_client = TestClient(app)
    second_client = TestClient(app)
    first_client.__enter__()
    second_client.__enter__()
    try:
        first_user = login_existing_user(first_client, email)
        second_user = login_existing_user(second_client, email)

        def submit_export(
            client: TestClient,
            logged_in_user: LoggedInUser,
        ):
            return client.post(
                f"/api/v1/workspaces/{workspace_id}/exports",
                headers={
                    "X-CSRF-Token": logged_in_user.csrf_token,
                    "Idempotency-Key": idempotency_key,
                },
            )

        with ThreadPoolExecutor(max_workers=2) as pool:
            responses = list(
                pool.map(
                    submit_export,
                    (first_client, second_client),
                    (first_user, second_user),
                )
            )
    finally:
        second_client.__exit__(None, None, None)
        first_client.__exit__(None, None, None)

    assert [response.status_code for response in responses] == [202, 202]
    assert responses[0].json()["id"] == responses[1].json()["id"]

    engine = create_engine(migrated_database_url)
    try:
        with engine.connect() as connection:
            count = connection.execute(
                text(
                    """
                    SELECT COUNT(*)
                    FROM idempotency_keys AS i
                    JOIN exports AS e ON e.id = i.export_id
                    JOIN jobs AS j ON j.export_id = e.id
                    WHERE i.user_id = :user_id
                      AND i.key = :idempotency_key
                    """
                ),
                {
                    "user_id": user.id,
                    "idempotency_key": idempotency_key,
                },
            ).scalar_one()
    finally:
        engine.dispose()

    assert count == 1
