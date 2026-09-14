from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import select, tuple_, update
from sqlalchemy.orm import Session

from taskforge.config import Settings
from taskforge.db_models import AuditEventRow, ProjectRow, TaskRow, WorkspaceRow
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

    def list_projects(
        self,
        page_size: int,
        name_contains: str | None = None,
    ) -> list[ProjectRead]:
        statement = select(ProjectRow).where(
            ProjectRow.workspace_id == self.settings.default_workspace_id
        )

        if name_contains is not None:
            statement = statement.where(ProjectRow.name.ilike(f"%{name_contains}%"))

        statement = statement.order_by(ProjectRow.created_at).limit(page_size)

        rows = self.session.scalars(statement).all()
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
            version=1,
        )
        self.session.add(task)
        self.session.flush()
        return self._task_read(task)

    def list_tasks(
        self,
        project_id: UUID,
        page_size: int,
        after_created_at: datetime | None = None,
        after_id: UUID | None = None,
    ) -> list[TaskRead] | None:
        if self._get_project_row(project_id) is None:
            return None

        statement = select(TaskRow).where(TaskRow.project_id == project_id)

        if after_created_at is not None and after_id is not None:
            statement = statement.where(
                tuple_(TaskRow.created_at, TaskRow.id) > (after_created_at, after_id)
            )

        statement = statement.order_by(TaskRow.created_at, TaskRow.id).limit(page_size)

        rows = self.session.scalars(statement).all()
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
        values: dict[str, object] = {"version": TaskRow.version + 1}
        if payload.title is not None:
            values["title"] = payload.title
        if payload.status is not None:
            values["status"] = payload.status.value

        row = self.session.scalar(
            update(TaskRow)
            .where(
                TaskRow.project_id == project_id,
                TaskRow.id == task_id,
                TaskRow.version == payload.expected_version,
            )
            .values(**values)
            .returning(TaskRow)
        )
        if row is None:
            return None

        self.session.add(
            AuditEventRow(
                id=uuid4(),
                task_id=row.id,
                event_type="task.updated",
                previous_version=payload.expected_version,
                new_version=row.version,
            )
        )
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
            version=row.version,
            created_at=row.created_at,
        )
