from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from taskforge.models import (
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
    TaskCreate,
    TaskRead,
    TaskStatus,
    TaskUpdate,
)


class InvalidStateTransitionError(Exception):
    pass


@dataclass
class InMemoryStore:
    projects: dict[UUID, ProjectRead] = field(default_factory=dict)
    tasks: dict[UUID, dict[UUID, TaskRead]] = field(default_factory=dict)

    def create_project(self, payload: ProjectCreate) -> ProjectRead:
        project = ProjectRead(
            id=uuid4(),
            name=payload.name,
            created_at=datetime.now(UTC),
        )
        self.projects[project.id] = project
        self.tasks[project.id] = {}
        return project

    def list_projects(self, page_size: int) -> list[ProjectRead]:
        ordered_projects = sorted(
            self.projects.values(),
            key=lambda project: project.created_at,
        )
        return ordered_projects[:page_size]

    def get_project(self, project_id: UUID) -> ProjectRead | None:
        return self.projects.get(project_id)

    def update_project(
        self,
        project_id: UUID,
        payload: ProjectUpdate,
    ) -> ProjectRead | None:
        project = self.projects.get(project_id)
        if project is None:
            return None
        updated = project.model_copy(update={"name": payload.name})
        self.projects[project_id] = updated
        return updated

    def delete_project(self, project_id: UUID) -> bool:
        if project_id not in self.projects:
            return False
        del self.projects[project_id]
        del self.tasks[project_id]
        return True

    def create_task(self, project_id: UUID, payload: TaskCreate) -> TaskRead | None:
        if project_id not in self.projects:
            return None
        task = TaskRead(
            id=uuid4(),
            project_id=project_id,
            title=payload.title,
            status=payload.status,
            created_at=datetime.now(UTC),
        )
        self.tasks[project_id][task.id] = task
        return task

    def list_tasks(self, project_id: UUID, page_size: int) -> list[TaskRead] | None:
        project_tasks = self.tasks.get(project_id)
        if project_tasks is None:
            return None
        ordered_tasks = sorted(
            project_tasks.values(),
            key=lambda task: task.created_at,
        )
        return ordered_tasks[:page_size]

    def get_task(self, project_id: UUID, task_id: UUID) -> TaskRead | None:
        return self.tasks.get(project_id, {}).get(task_id)

    def update_task(
        self,
        project_id: UUID,
        task_id: UUID,
        payload: TaskUpdate,
    ) -> TaskRead | None:
        task = self.get_task(project_id, task_id)
        if task is None:
            return None
        if task.status == TaskStatus.todo and payload.status == TaskStatus.done:
            raise InvalidStateTransitionError
        changes = payload.model_dump(exclude_unset=True)
        updated = task.model_copy(update=changes)
        self.tasks[project_id][task_id] = updated
        return updated

    def delete_task(self, project_id: UUID, task_id: UUID) -> bool:
        project_tasks = self.tasks.get(project_id)
        if project_tasks is None or task_id not in project_tasks:
            return False
        del project_tasks[task_id]
        return True
