from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, text, update
from test_authorization import (
    LoggedInUser,
    create_workspace,
    create_workspace_project,
    create_workspace_task,
    login_existing_user,
    register_and_login,
)

from taskforge.config import Settings
from taskforge.db_models import JobRow
from taskforge.jobs import (
    ExportRepository,
    RetryableExportError,
    cleanup_expired_export_artifacts,
    csv_safe_cell,
    run_one_export,
)
from taskforge.main import create_app


def make_settings(url: str, export_storage_dir: str) -> Settings:
    return Settings(
        environment="test",
        storage_backend="postgres",
        database_url=url,
        database_pool_size=2,
        database_max_overflow=0,
        database_pool_timeout_seconds=2,
        export_storage_dir=export_storage_dir,
    )


def create_export(
    client: TestClient,
    workspace_id: str,
    user: LoggedInUser,
    idempotency_key: str | None = None,
) -> dict:
    if idempotency_key is None:
        idempotency_key = str(uuid4())

    response = client.post(
        f"/api/v1/workspaces/{workspace_id}/exports",
        headers={
            "X-CSRF-Token": user.csrf_token,
            "Idempotency-Key": idempotency_key,
        },
    )
    assert response.status_code == 202
    return response.json()


def test_export_acceptance_commits_export_and_job_together(
    migrated_database_url: str,
    tmp_path: Path,
) -> None:
    app = create_app(make_settings(migrated_database_url, str(tmp_path)))

    with TestClient(app) as client:
        owner = register_and_login(client, "owner@example.com")
        workspace_id = create_workspace(client, owner)
        export = create_export(client, workspace_id, owner)

        status_response = client.get(f"/api/v1/exports/{export['id']}")

    assert status_response.status_code == 200
    assert status_response.json()["status"] == "pending"
    assert status_response.headers["content-type"].startswith("application/json")

    engine = create_engine(migrated_database_url)
    try:
        with engine.connect() as connection:
            row = connection.execute(
                text(
                    """
                    SELECT e.status AS export_status, j.status AS job_status
                    FROM exports AS e
                    JOIN jobs AS j ON j.export_id = e.id
                    WHERE e.id = :export_id
                    """
                ),
                {"export_id": export["id"]},
            ).one()
    finally:
        engine.dispose()

    assert row.export_status == "pending"
    assert row.job_status == "pending"


def test_export_status_is_tenant_scoped(
    migrated_database_url: str,
    tmp_path: Path,
) -> None:
    app = create_app(make_settings(migrated_database_url, str(tmp_path)))

    with TestClient(app) as client:
        owner = register_and_login(client, "owner@example.com")
        workspace_id = create_workspace(client, owner)
        export = create_export(client, workspace_id, owner)
        _outsider = register_and_login(client, "outsider@example.com")

        response = client.get(f"/api/v1/exports/{export['id']}")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "export_not_found"


def test_worker_completes_export_and_writes_csv(
    migrated_database_url: str,
    tmp_path: Path,
) -> None:
    app = create_app(make_settings(migrated_database_url, str(tmp_path)))

    with TestClient(app) as client:
        owner = register_and_login(client, "owner@example.com")
        workspace_id = create_workspace(client, owner)
        project = create_workspace_project(client, workspace_id, owner)
        create_workspace_task(client, workspace_id, project["id"], owner)
        export = create_export(client, workspace_id, owner)

        assert run_one_export(
            app.state.session_factory,
            str(tmp_path),
        )

        response = client.get(f"/api/v1/exports/{export['id']}")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "succeeded"
    assert body["output_reference"] == f"exports/export_{export['id']}_attempt_1.csv"
    output_path = tmp_path / f"export_{UUID(export['id'])}_attempt_1.csv"
    assert output_path.read_text(encoding="utf-8").splitlines() == [
        "project,task,status",
        "Launch plan,Draft checklist,todo",
    ]


def test_owner_can_download_succeeded_export(
    migrated_database_url: str,
    tmp_path: Path,
) -> None:
    app = create_app(make_settings(migrated_database_url, str(tmp_path)))

    with TestClient(app) as client:
        owner = register_and_login(client, "download-owner@example.com")
        workspace_id = create_workspace(client, owner)
        project = create_workspace_project(client, workspace_id, owner)
        create_workspace_task(client, workspace_id, project["id"], owner)
        export = create_export(client, workspace_id, owner)

        assert run_one_export(
            app.state.session_factory,
            str(tmp_path),
        )

        response = client.get(f"/api/v1/exports/{export['id']}/download")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert response.text.splitlines() == [
        "project,task,status",
        "Launch plan,Draft checklist,todo",
    ]


def test_outsider_cannot_download_export(
    migrated_database_url: str,
    tmp_path: Path,
) -> None:
    app = create_app(make_settings(migrated_database_url, str(tmp_path)))

    with TestClient(app) as client:
        owner = register_and_login(client, "download-owner-2@example.com")
        workspace_id = create_workspace(client, owner)
        export = create_export(client, workspace_id, owner)

        register_and_login(client, "download-outsider@example.com")
        response = client.get(f"/api/v1/exports/{export['id']}/download")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "export_not_found"


def test_pending_export_cannot_be_downloaded(
    migrated_database_url: str,
    tmp_path: Path,
) -> None:
    app = create_app(make_settings(migrated_database_url, str(tmp_path)))

    with TestClient(app) as client:
        owner = register_and_login(client, "download-owner-3@example.com")
        workspace_id = create_workspace(client, owner)
        export = create_export(client, workspace_id, owner)

        response = client.get(f"/api/v1/exports/{export['id']}/download")

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "export_not_ready"


def test_missing_succeeded_artifact_returns_server_error(
    migrated_database_url: str,
    tmp_path: Path,
) -> None:
    app = create_app(make_settings(migrated_database_url, str(tmp_path)))

    with TestClient(app) as client:
        owner = register_and_login(client, "download-owner-4@example.com")
        workspace_id = create_workspace(client, owner)
        export = create_export(client, workspace_id, owner)

        assert run_one_export(
            app.state.session_factory,
            str(tmp_path),
        )
        output_path = tmp_path / f"export_{UUID(export['id'])}_attempt_1.csv"
        output_path.unlink()

        response = client.get(f"/api/v1/exports/{export['id']}/download")

    assert response.status_code == 500
    assert response.json()["error"]["code"] == "export_artifact_missing"


def test_csv_formula_prefixes_are_neutralized() -> None:
    assert csv_safe_cell("=SUM(A1:A2)") == "'=SUM(A1:A2)"
    assert csv_safe_cell("+123") == "'+123"
    assert csv_safe_cell("-123") == "'-123"
    assert csv_safe_cell("@command") == "'@command"
    assert csv_safe_cell("ordinary text") == "ordinary text"


def test_download_rejects_traversal_output_reference(
    migrated_database_url: str,
    tmp_path: Path,
) -> None:
    app = create_app(make_settings(migrated_database_url, str(tmp_path)))

    with TestClient(app) as client:
        owner = register_and_login(client, "download-owner-5@example.com")
        workspace_id = create_workspace(client, owner)
        export = create_export(client, workspace_id, owner)

        assert run_one_export(
            app.state.session_factory,
            str(tmp_path),
        )

        engine = create_engine(migrated_database_url)
        try:
            with engine.begin() as connection:
                connection.execute(
                    text(
                        "UPDATE exports "
                        "SET output_location = :output_location "
                        "WHERE id = :export_id"
                    ),
                    {
                        "output_location": "exports/../outside.csv",
                        "export_id": export["id"],
                    },
                )
        finally:
            engine.dispose()

        response = client.get(f"/api/v1/exports/{export['id']}/download")

    assert response.status_code == 500
    assert response.json()["error"]["code"] == "export_artifact_missing"


def test_retention_cleanup_expires_old_export_artifact(
    migrated_database_url: str,
    tmp_path: Path,
) -> None:
    app = create_app(make_settings(migrated_database_url, str(tmp_path)))

    with TestClient(app) as client:
        owner = register_and_login(client, "download-owner-6@example.com")
        workspace_id = create_workspace(client, owner)
        export = create_export(client, workspace_id, owner)

        assert run_one_export(
            app.state.session_factory,
            str(tmp_path),
        )
        output_path = tmp_path / f"export_{UUID(export['id'])}_attempt_1.csv"
        assert output_path.is_file()

        engine = create_engine(migrated_database_url)
        try:
            with engine.begin() as connection:
                connection.execute(
                    text(
                        "UPDATE exports "
                        "SET completed_at = :completed_at "
                        "WHERE id = :export_id"
                    ),
                    {
                        "completed_at": datetime.now(UTC) - timedelta(days=2),
                        "export_id": export["id"],
                    },
                )
        finally:
            engine.dispose()

        removed = cleanup_expired_export_artifacts(
            app.state.session_factory,
            str(tmp_path),
            timedelta(hours=24),
        )
        response = client.get(f"/api/v1/exports/{export['id']}/download")

    assert removed == 1
    assert not output_path.exists()
    assert response.status_code == 410
    assert response.json()["error"]["code"] == "export_expired"


def test_worker_records_failure(
    migrated_database_url: str,
    tmp_path: Path,
) -> None:
    app = create_app(make_settings(migrated_database_url, str(tmp_path)))

    with TestClient(app) as client:
        owner = register_and_login(client, "owner@example.com")
        workspace_id = create_workspace(client, owner)
        export = create_export(client, workspace_id, owner)

        def fail_generator(_session, _workspace_id, _path) -> None:
            raise RuntimeError("synthetic generator failure")

        assert run_one_export(
            app.state.session_factory,
            str(tmp_path),
            generator=fail_generator,
        )
        response = client.get(f"/api/v1/exports/{export['id']}")

    assert response.status_code == 200
    assert response.json()["status"] == "failed"
    assert response.json()["error"] == "Export generation failed"


def test_retryable_failure_is_retried_with_attempt_specific_output(
    migrated_database_url: str,
    tmp_path: Path,
) -> None:
    app = create_app(make_settings(migrated_database_url, str(tmp_path)))

    with TestClient(app) as client:
        owner = register_and_login(client, "retry-owner@example.com")
        workspace_id = create_workspace(client, owner)
        export = create_export(client, workspace_id, owner)

        def retryable_generator(_session, _workspace_id, _path) -> None:
            raise RetryableExportError("temporary failure")

        assert run_one_export(
            app.state.session_factory,
            str(tmp_path),
            generator=retryable_generator,
        )

        with app.state.session_factory() as session:
            retry_job = session.scalar(
                select(JobRow).where(JobRow.export_id == UUID(export["id"]))
            )
            assert retry_job is not None
            assert retry_job.status == "pending"
            assert retry_job.attempt == 1
            assert retry_job.next_retry_at is not None
            session.execute(
                update(JobRow)
                .where(JobRow.id == retry_job.id)
                .values(next_retry_at=datetime.now(UTC) - timedelta(seconds=1))
            )
            session.commit()

        assert run_one_export(
            app.state.session_factory,
            str(tmp_path),
        )

        response = client.get(f"/api/v1/exports/{export['id']}")

    assert response.status_code == 200
    assert response.json()["status"] == "succeeded"
    assert response.json()["output_reference"] == (
        f"exports/export_{export['id']}_attempt_2.csv"
    )
    assert (tmp_path / f"export_{UUID(export['id'])}_attempt_2.csv").exists()
    assert not list(tmp_path.glob("*.tmp"))


def test_failed_generation_cleans_temporary_artifact(
    migrated_database_url: str,
    tmp_path: Path,
) -> None:
    app = create_app(make_settings(migrated_database_url, str(tmp_path)))

    with TestClient(app) as client:
        owner = register_and_login(client, "artifact-owner@example.com")
        workspace_id = create_workspace(client, owner)
        create_export(client, workspace_id, owner)

        def partial_failure(_session, _workspace_id, path: Path) -> None:
            path.write_text("partial", encoding="utf-8")
            raise RuntimeError("synthetic failure")

        assert run_one_export(
            app.state.session_factory,
            str(tmp_path),
            generator=partial_failure,
        )

    assert not list(tmp_path.iterdir())


def test_concurrent_workers_claim_different_jobs(
    migrated_database_url: str,
    tmp_path: Path,
) -> None:
    app = create_app(make_settings(migrated_database_url, str(tmp_path)))

    with TestClient(app) as client:
        owner = register_and_login(client, "owner@example.com")
        workspace_id = create_workspace(client, owner)
        first = create_export(client, workspace_id, owner)
        second = create_export(client, workspace_id, owner)

    def claim_one():
        with app.state.session_factory() as session:
            repository = ExportRepository(session)
            claim = repository.claim_one(30)
            session.commit()
            return claim

    with ThreadPoolExecutor(max_workers=2) as pool:
        claims = list(pool.map(lambda _worker: claim_one(), range(2)))

    assert all(claims)
    assert {claim.export_id for claim in claims} == {
        UUID(first["id"]),
        UUID(second["id"]),
    }
    assert claims[0].owner_token != claims[1].owner_token


def test_expired_owner_cannot_complete_after_reclaim(
    migrated_database_url: str,
    tmp_path: Path,
) -> None:
    app = create_app(make_settings(migrated_database_url, str(tmp_path)))

    with TestClient(app) as client:
        owner = register_and_login(client, "owner@example.com")
        workspace_id = create_workspace(client, owner)
        export = create_export(client, workspace_id, owner)

    with app.state.session_factory() as session:
        first_repository = ExportRepository(session)
        first_claim = first_repository.claim_one(30)
        assert first_claim is not None
        session.commit()

    with app.state.session_factory() as session:
        session.execute(
            update(JobRow)
            .where(JobRow.id == first_claim.job_id)
            .values(lease_expires_at=datetime.now(UTC) - timedelta(seconds=1))
        )
        session.commit()

    with app.state.session_factory() as session:
        second_repository = ExportRepository(session)
        second_claim = second_repository.claim_one(30)
        assert second_claim is not None
        session.commit()

    assert second_claim.export_id == UUID(export["id"])
    assert second_claim.owner_token != first_claim.owner_token

    with app.state.session_factory() as session:
        old_repository = ExportRepository(session)
        assert not old_repository.complete(
            first_claim,
            "exports/stale.csv",
            "a" * 64,
        )
        session.rollback()

    with app.state.session_factory() as session:
        current_repository = ExportRepository(session)
        assert current_repository.complete(
            second_claim,
            "exports/current.csv",
            "b" * 64,
        )
        session.commit()

    with TestClient(app) as client:
        login_existing_user(client, "owner@example.com")
        response = client.get(f"/api/v1/exports/{export['id']}")

    assert response.status_code == 200
    assert response.json()["status"] == "succeeded"
    assert response.json()["output_reference"] == "exports/current.csv"
