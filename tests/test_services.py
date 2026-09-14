import pytest

from taskforge.errors import InvalidStateTransitionError, ProjectNotFoundError
from taskforge.models import ProjectCreate, TaskCreate, TaskStatus, TaskUpdate
from taskforge.services import TaskForgeService
from taskforge.store import InMemoryStore


def make_service() -> TaskForgeService:
    return TaskForgeService(InMemoryStore())


def test_service_owns_task_status_transition_rule() -> None:
    service = make_service()
    project = service.create_project(ProjectCreate(name="Launch plan"))
    task = service.create_task(project.id, TaskCreate(title="Draft checklist"))

    with pytest.raises(InvalidStateTransitionError):
        service.update_task(
            project.id,
            task.id,
            TaskUpdate(status=TaskStatus.done, expected_version=task.version),
        )

    unchanged = service.get_task(project.id, task.id)
    assert unchanged.status == TaskStatus.todo


def test_store_does_not_enforce_task_status_transition_rule() -> None:
    store = InMemoryStore()
    project = store.create_project(ProjectCreate(name="Launch plan"))
    task = store.create_task(project.id, TaskCreate(title="Draft checklist"))
    assert task is not None

    updated = store.update_task(
        project.id,
        task.id,
        TaskUpdate(status=TaskStatus.done, expected_version=task.version),
    )

    assert updated is not None
    assert updated.status == TaskStatus.done


def test_service_reports_missing_project_before_storage_update() -> None:
    service = make_service()

    with pytest.raises(ProjectNotFoundError):
        service.create_task(
            project_id="00000000-0000-4000-8000-000000000001",
            payload=TaskCreate(title="No parent"),
        )
