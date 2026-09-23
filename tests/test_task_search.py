from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from taskforge.authorization_repository import AuthorizationRepository
from taskforge.authorization_service import AuthorizationService
from taskforge.db_models import (
    MembershipRow,
    ProjectRow,
    TaskRow,
    UserRow,
    WorkspaceRow,
)
from taskforge.errors import WorkspaceNotFoundError
from taskforge.models import UserRead


def test_search_workspace_tasks_is_tenant_scoped(
    migrated_database_url: str,
) -> None:
    engine = create_engine(migrated_database_url)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)

    user_id = uuid4()
    workspace_a_id = uuid4()
    workspace_b_id = uuid4()
    project_a_id = uuid4()
    project_b_id = uuid4()
    task_a_id = uuid4()
    task_b_id = uuid4()

    with session_factory() as session:
        session.add_all(
            [
                UserRow(
                    id=user_id,
                    email="searcher@example.com",
                    password_hash="test-password-hash",
                ),
                WorkspaceRow(id=workspace_a_id, name="Workspace A"),
                WorkspaceRow(id=workspace_b_id, name="Workspace B"),
            ]
        )
        session.flush()

        session.add_all(
            [
                MembershipRow(
                    id=uuid4(),
                    user_id=user_id,
                    workspace_id=workspace_a_id,
                    role="owner",
                ),
                ProjectRow(
                    id=project_a_id,
                    workspace_id=workspace_a_id,
                    name="Project A",
                ),
                ProjectRow(
                    id=project_b_id,
                    workspace_id=workspace_b_id,
                    name="Project B",
                ),
            ]
        )
        session.flush()

        session.add_all(
            [
                TaskRow(
                    id=task_a_id,
                    project_id=project_a_id,
                    title="Deploy API",
                    status="todo",
                ),
                TaskRow(
                    id=task_b_id,
                    project_id=project_b_id,
                    title="Deploy secrets",
                    status="todo",
                ),
            ]
        )
        session.commit()

        repository = AuthorizationRepository(session)

        results = repository.search_workspace_tasks_for_user(
            user_id=user_id,
            workspace_id=workspace_a_id,
            query="deploy",
            limit=20,
        )

    engine.dispose()

    assert results is not None
    assert [task.id for task in results] == [task_a_id]
    assert task_b_id not in {task.id for task in results}


def test_search_workspace_tasks_rejects_non_member(
    migrated_database_url: str,
) -> None:
    engine = create_engine(migrated_database_url)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)

    user_id = uuid4()
    workspace_id = uuid4()
    created_at = datetime.now(timezone.utc)

    with session_factory() as session:
        session.add_all(
            [
                UserRow(
                    id=user_id,
                    email="outsider@example.com",
                    password_hash="test-password-hash",
                ),
                WorkspaceRow(id=workspace_id, name="Private workspace"),
            ]
        )
        session.commit()

        service = AuthorizationService(AuthorizationRepository(session))
        current_user = UserRead(
            id=user_id,
            email="outsider@example.com",
            created_at=created_at,
        )

        with pytest.raises(WorkspaceNotFoundError):
            service.search_workspace_tasks(
                current_user=current_user,
                workspace_id=workspace_id,
                query="deploy",
                limit=20,
            )

    engine.dispose()


def test_task_title_trigram_index_exists(
    migrated_database_url: str,
) -> None:
    engine = create_engine(migrated_database_url)

    with engine.connect() as connection:
        index_definition = connection.execute(
            text(
                """
            SELECT indexdef
            FROM pg_indexes
            WHERE tablename = 'tasks'
              AND indexname = 'ix_tasks_title_trgm'
                """
            )
        ).scalar_one()

    engine.dispose()

    assert "USING gin" in index_definition
    assert "gin_trgm_ops" in index_definition
