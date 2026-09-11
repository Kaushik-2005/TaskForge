from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from taskforge.config import Settings
from taskforge.main import create_app
from taskforge.models import ProjectCreate, TaskCreate
from taskforge.repositories import PostgresStore
from taskforge.services import TaskForgeService


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


def test_postgres_project_list_filters_by_name(
    migrated_database_url: str,
) -> None:
    engine = create_engine(migrated_database_url)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    settings = make_settings(migrated_database_url)

    with session_factory() as session:
        service = TaskForgeService(PostgresStore(session, settings))

        service.create_project(ProjectCreate(name="Launch plan"))
        service.create_project(ProjectCreate(name="Backend work"))
        service.create_project(ProjectCreate(name="PLAN review"))

        session.commit()

    with session_factory() as session:
        service = TaskForgeService(PostgresStore(session, settings))

        projects = service.list_projects(
            page_size=10,
            name_contains="plan",
        )

    engine.dispose()

    assert [project.name for project in projects] == [
        "Launch plan",
        "PLAN review",
    ]


def test_postgres_project_filter_respects_page_size(
    migrated_database_url: str,
) -> None:
    engine = create_engine(migrated_database_url)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    settings = make_settings(migrated_database_url)

    with session_factory() as session:
        service = TaskForgeService(PostgresStore(session, settings))

        service.create_project(ProjectCreate(name="Launch plan"))
        service.create_project(ProjectCreate(name="Planning notes"))
        service.create_project(ProjectCreate(name="PLAN review"))

        session.commit()

    with session_factory() as session:
        service = TaskForgeService(PostgresStore(session, settings))

        projects = service.list_projects(
            page_size=2,
            name_contains="plan",
        )

    engine.dispose()

    assert len(projects) == 2
    assert all("plan" in project.name.lower() for project in projects)


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
