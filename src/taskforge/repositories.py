from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from taskforge.config import Settings
from taskforge.db_models import ProjectRow, TaskRow, WorkspaceRow
from taskforge.models import (
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
    TaskCreate,
    TaskRead,
    TaskStatus,
    TaskUpdate,
)


class PostgresStore:
    def __init__(self, session: Session, settings: Settings) -> None:
        self.session = session
        self.settings = settings

    def _ensure_default_workspace(self) -> None:
        workspace = self.session.get(WorkspaceRow, self.settings.default_workspace_id)
        if workspace is not None:
            return
        self.session.add(
            WorkspaceRow(
                id=self.settings.default_workspace_id,
                name=self.settings.default_workspace_name,
            )
        )
        self.session.flush()

    def create_project(self, payload: ProjectCreate) -> ProjectRead:
        self._ensure_default_workspace()
        project = ProjectRow(
            id=uuid4(),
            workspace_id=self.settings.default_workspace_id,
            name=payload.name,
        )
        self.session.add(project)
        self.session.flush()
        return self._project_read(project)

    def list_projects(self, page_size: int) -> list[ProjectRead]:
        rows = self.session.scalars(
            select(ProjectRow)
            .where(ProjectRow.workspace_id == self.settings.default_workspace_id)
            .order_by(ProjectRow.created_at)
            .limit(page_size)
        ).all()
        return [self._project_read(row) for row in rows]

    def get_project(self, project_id: UUID) -> ProjectRead | None:
        row = self._get_project_row(project_id)
        if row is None:
            return None
        return self._project_read(row)

    def update_project(
        self,
        project_id: UUID,
        payload: ProjectUpdate,
    ) -> ProjectRead | None:
        row = self._get_project_row(project_id)
        if row is None:
            return None
        row.name = payload.name
        self.session.flush()
        return self._project_read(row)

    def delete_project(self, project_id: UUID) -> bool:
        row = self._get_project_row(project_id)
        if row is None:
            return False
        self.session.delete(row)
        self.session.flush()
        return True

    def create_task(self, project_id: UUID, payload: TaskCreate) -> TaskRead | None:
        if self._get_project_row(project_id) is None:
            return None
        task = TaskRow(
            id=uuid4(),
            project_id=project_id,
            title=payload.title,
            status=payload.status.value,
        )
        self.session.add(task)
        self.session.flush()
        return self._task_read(task)

    def list_tasks(self, project_id: UUID, page_size: int) -> list[TaskRead] | None:
        if self._get_project_row(project_id) is None:
            return None
        rows = self.session.scalars(
            select(TaskRow)
            .where(TaskRow.project_id == project_id)
            .order_by(TaskRow.created_at)
            .limit(page_size)
        ).all()
        return [self._task_read(row) for row in rows]

    def get_task(self, project_id: UUID, task_id: UUID) -> TaskRead | None:
        row = self.session.scalar(
            select(TaskRow).where(
                TaskRow.project_id == project_id,
                TaskRow.id == task_id,
            )
        )
        if row is None:
            return None
        return self._task_read(row)

    def update_task(
        self,
        project_id: UUID,
        task_id: UUID,
        payload: TaskUpdate,
    ) -> TaskRead | None:
        row = self.session.scalar(
            select(TaskRow).where(
                TaskRow.project_id == project_id,
                TaskRow.id == task_id,
            )
        )
        if row is None:
            return None
        if payload.title is not None:
            row.title = payload.title
        if payload.status is not None:
            row.status = payload.status.value
        self.session.flush()
        return self._task_read(row)

    def delete_task(self, project_id: UUID, task_id: UUID) -> bool:
        row = self.session.scalar(
            select(TaskRow).where(
                TaskRow.project_id == project_id,
                TaskRow.id == task_id,
            )
        )
        if row is None:
            return False
        self.session.delete(row)
        self.session.flush()
        return True

    def _get_project_row(self, project_id: UUID) -> ProjectRow | None:
        return self.session.scalar(
            select(ProjectRow).where(
                ProjectRow.workspace_id == self.settings.default_workspace_id,
                ProjectRow.id == project_id,
            )
        )

    @staticmethod
    def _project_read(row: ProjectRow) -> ProjectRead:
        return ProjectRead(id=row.id, name=row.name, created_at=row.created_at)

    @staticmethod
    def _task_read(row: TaskRow) -> TaskRead:
        return TaskRead(
            id=row.id,
            project_id=row.project_id,
            title=row.title,
            status=TaskStatus(row.status),
            created_at=row.created_at,
        )
