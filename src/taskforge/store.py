from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from taskforge.models import (
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
    TaskCreate,
    TaskRead,
    TaskUpdate,
)


@dataclass
class InMemoryStore:
    projects: dict[str, ProjectRead] = field(default_factory=dict)
    tasks: dict[str, dict[str, TaskRead]] = field(default_factory=dict)

    def create_project(self, payload: ProjectCreate) -> ProjectRead:
        project = ProjectRead(
            id=str(uuid4()),
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

    def get_project(self, project_id: str) -> ProjectRead | None:
        return self.projects.get(project_id)

    def update_project(
        self,
        project_id: str,
        payload: ProjectUpdate,
    ) -> ProjectRead | None:
        project = self.projects.get(project_id)
        if project is None:
            return None
        updated = project.model_copy(update={"name": payload.name})
        self.projects[project_id] = updated
        return updated

    def delete_project(self, project_id: str) -> bool:
        if project_id not in self.projects:
            return False
        del self.projects[project_id]
        del self.tasks[project_id]
        return True

    def create_task(self, project_id: str, payload: TaskCreate) -> TaskRead | None:
        if project_id not in self.projects:
            return None
        task = TaskRead(
            id=str(uuid4()),
            project_id=project_id,
            title=payload.title,
            status=payload.status,
            created_at=datetime.now(UTC),
        )
        self.tasks[project_id][task.id] = task
        return task

    def list_tasks(self, project_id: str, page_size: int) -> list[TaskRead] | None:
        project_tasks = self.tasks.get(project_id)
        if project_tasks is None:
            return None
        ordered_tasks = sorted(
            project_tasks.values(),
            key=lambda task: task.created_at,
        )
        return ordered_tasks[:page_size]

    def get_task(self, project_id: str, task_id: str) -> TaskRead | None:
        return self.tasks.get(project_id, {}).get(task_id)

    def update_task(
        self,
        project_id: str,
        task_id: str,
        payload: TaskUpdate,
    ) -> TaskRead | None:
        task = self.get_task(project_id, task_id)
        if task is None:
            return None
        changes = payload.model_dump(exclude_unset=True)
        if not changes:
            return task
        updated = task.model_copy(update=changes)
        self.tasks[project_id][task_id] = updated
        return updated

    def delete_task(self, project_id: str, task_id: str) -> bool:
        project_tasks = self.tasks.get(project_id)
        if project_tasks is None or task_id not in project_tasks:
            return False
        del project_tasks[task_id]
        return True
