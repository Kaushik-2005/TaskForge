from datetime import datetime
from typing import Protocol
from uuid import UUID

from taskforge.errors import (
    InvalidStateTransitionError,
    ProjectNotFoundError,
    StaleTaskVersionError,
    TaskNotFoundError,
)
from taskforge.models import (
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
    TaskCreate,
    TaskRead,
    TaskStatus,
    TaskUpdate,
)


class TaskForgeStore(Protocol):
    def create_project(self, payload: ProjectCreate) -> ProjectRead: ...
    def list_projects(
        self,
        page_size: int,
        name_contains: str | None = None,
    ) -> list[ProjectRead]: ...
    def get_project(self, project_id: UUID) -> ProjectRead | None: ...
    def update_project(
        self,
        project_id: UUID,
        payload: ProjectUpdate,
    ) -> ProjectRead | None: ...
    def delete_project(self, project_id: UUID) -> bool: ...
    def create_task(self, project_id: UUID, payload: TaskCreate) -> TaskRead | None: ...
    def list_tasks(
        self,
        project_id: UUID,
        page_size: int,
        after_created_at: datetime | None = None,
        after_id: UUID | None = None,
    ) -> list[TaskRead] | None: ...
    def get_task(self, project_id: UUID, task_id: UUID) -> TaskRead | None: ...
    def update_task(
        self,
        project_id: UUID,
        task_id: UUID,
        payload: TaskUpdate,
    ) -> TaskRead | None: ...
    def delete_task(self, project_id: UUID, task_id: UUID) -> bool: ...


class TaskForgeService:
    def __init__(self, store: TaskForgeStore) -> None:
        self.store = store

    def create_project(self, payload: ProjectCreate) -> ProjectRead:
        return self.store.create_project(payload)

    def list_projects(
        self,
        page_size: int,
        name_contains: str | None = None,
    ) -> list[ProjectRead]:
        return self.store.list_projects(
            page_size,
            name_contains=name_contains,
        )

    def get_project(self, project_id: UUID) -> ProjectRead:
        project = self.store.get_project(project_id)
        if project is None:
            raise ProjectNotFoundError
        return project

    def update_project(self, project_id: UUID, payload: ProjectUpdate) -> ProjectRead:
        project = self.store.update_project(project_id, payload)
        if project is None:
            raise ProjectNotFoundError
        return project

    def delete_project(self, project_id: UUID) -> None:
        if not self.store.delete_project(project_id):
            raise ProjectNotFoundError

    def create_task(self, project_id: UUID, payload: TaskCreate) -> TaskRead:
        task = self.store.create_task(project_id, payload)
        if task is None:
            raise ProjectNotFoundError
        return task

    def list_tasks(
        self,
        project_id: UUID,
        page_size: int,
        after_created_at: datetime | None = None,
        after_id: UUID | None = None,
    ) -> list[TaskRead] | None:
        tasks = self.store.list_tasks(
            project_id,
            page_size,
            after_created_at=after_created_at,
            after_id=after_id,
        )
        if tasks is None:
            raise ProjectNotFoundError
        return tasks

    def get_task(self, project_id: UUID, task_id: UUID) -> TaskRead:
        self.get_project(project_id)
        task = self.store.get_task(project_id, task_id)
        if task is None:
            raise TaskNotFoundError
        return task

    def update_task(
        self,
        project_id: UUID,
        task_id: UUID,
        payload: TaskUpdate,
    ) -> TaskRead:
        task = self.get_task(project_id, task_id)
        if task.status == TaskStatus.todo and payload.status == TaskStatus.done:
            raise InvalidStateTransitionError
        updated = self.store.update_task(project_id, task_id, payload)
        if updated is None:
            raise StaleTaskVersionError
        return updated

    def delete_task(self, project_id: UUID, task_id: UUID) -> None:
        self.get_project(project_id)
        if not self.store.delete_task(project_id, task_id):
            raise TaskNotFoundError
