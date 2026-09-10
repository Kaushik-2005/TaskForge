from collections.abc import Generator
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

from taskforge.config import Settings
from taskforge.main import create_app
from taskforge.models import ProjectCreate, TaskCreate
from taskforge.repositories import PostgresStore
from taskforge.services import TaskForgeService

ADMIN_DATABASE_URL = (
    "postgresql+psycopg://taskforge:taskforge_dev_password@127.0.0.1:5433/postgres"
)


def database_url(database_name: str) -> str:
    return (
        "postgresql+psycopg://taskforge:taskforge_dev_password"
        f"@127.0.0.1:5433/{database_name}"
    )


@pytest.fixture
def migrated_database_url() -> Generator[str]:
    admin_engine = create_engine(ADMIN_DATABASE_URL, isolation_level="AUTOCOMMIT")
    database_name = f"taskforge_test_{uuid4().hex}"

    try:
        with admin_engine.connect() as connection:
            connection.execute(text(f'CREATE DATABASE "{database_name}"'))
    except OperationalError as exc:
        pytest.skip(f"PostgreSQL is not available for integration tests: {exc}")

    url = database_url(database_name)
    try:
        config = Config("alembic.ini")
        config.set_main_option("sqlalchemy.url", url)
        command.upgrade(config, "head")
        yield url
    finally:
        with admin_engine.connect() as connection:
            connection.execute(
                text(
                    "SELECT pg_terminate_backend(pid) "
                    "FROM pg_stat_activity "
                    "WHERE datname = :database_name AND pid <> pg_backend_pid()"
                ),
                {"database_name": database_name},
            )
            connection.execute(text(f'DROP DATABASE IF EXISTS "{database_name}"'))
        admin_engine.dispose()


def make_settings(url: str) -> Settings:
    return Settings(
        environment="test",
        storage_backend="postgres",
        database_url=url,
        database_pool_size=2,
        database_max_overflow=0,
        database_pool_timeout_seconds=2,
    )


def test_migration_from_empty_database_supports_repository_commit(
    migrated_database_url: str,
) -> None:
    engine = create_engine(migrated_database_url)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    settings = make_settings(migrated_database_url)

    with session_factory() as session:
        service = TaskForgeService(PostgresStore(session, settings))
        project = service.create_project(ProjectCreate(name="Persistent project"))
        service.create_task(project.id, TaskCreate(title="Persistent task"))
        session.commit()

    with session_factory() as session:
        service = TaskForgeService(PostgresStore(session, settings))
        projects = service.list_projects(page_size=10)
        tasks = service.list_tasks(project.id, page_size=10)

    engine.dispose()
    assert [item.name for item in projects] == ["Persistent project"]
    assert tasks is not None
    assert [item.title for item in tasks] == ["Persistent task"]


def test_failed_multi_step_write_rolls_back(migrated_database_url: str) -> None:
    engine = create_engine(migrated_database_url)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    settings = make_settings(migrated_database_url)

    with session_factory() as session:
        service = TaskForgeService(PostgresStore(session, settings))
        project = service.create_project(ProjectCreate(name="Rollback project"))
        service.create_task(project.id, TaskCreate(title="First task"))
        session.rollback()

    with session_factory() as session:
        service = TaskForgeService(PostgresStore(session, settings))
        assert service.list_projects(page_size=10) == []

    engine.dispose()


def test_postgres_api_persists_across_app_instances(migrated_database_url: str) -> None:
    settings = make_settings(migrated_database_url)

    with TestClient(create_app(settings)) as first_client:
        created = first_client.post("/api/v1/projects", json={"name": "API project"})
        assert created.status_code == 201

    with TestClient(create_app(settings)) as second_client:
        listed = second_client.get("/api/v1/projects")

    assert listed.status_code == 200
    assert [item["name"] for item in listed.json()] == ["API project"]
