from collections.abc import Generator
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

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
