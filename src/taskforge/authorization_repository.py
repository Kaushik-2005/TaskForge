from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import func, select, tuple_, update
from sqlalchemy.orm import Session

from taskforge.db_models import (
    AuditEventRow,
    MembershipRow,
    ProjectRow,
    TaskRow,
    UserRow,
    WorkspaceRow,
)
from taskforge.errors import (
    DuplicateMembershipError,
    LastOwnerError,
    PermissionDeniedError,
    UserNotFoundError,
)
from taskforge.models import (
    MembershipCreate,
    MembershipRead,
    MembershipUpdate,
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
    TaskCreate,
    TaskRead,
    TaskStatus,
    TaskUpdate,
    WorkspaceCreate,
    WorkspaceRead,
)


class AuthorizationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_workspace_for_owner(
        self,
        user_id: UUID,
        payload: WorkspaceCreate,
    ) -> WorkspaceRead:
        workspace = WorkspaceRow(
            id=uuid4(),
            name=payload.name,
        )
        self.session.add(workspace)
        self.session.flush()

        membership = MembershipRow(
            id=uuid4(),
            user_id=user_id,
            workspace_id=workspace.id,
            role="owner",
        )
        self.session.add(membership)
        self.session.flush()

        return self._workspace_read(workspace)

    def create_membership_for_user(
        self,
        current_user_id: UUID,
        workspace_id: UUID,
        payload: MembershipCreate,
    ) -> MembershipRead | None:
        current_role = self.workspace_role_for_user(current_user_id, workspace_id)
        if current_role is None:
            return None
        if current_role not in {"owner", "admin"}:
            raise PermissionDeniedError

        user = self.session.scalar(
            select(UserRow).where(UserRow.email == payload.email)
        )
        if user is None:
            raise UserNotFoundError

        existing = self.session.scalar(
            select(MembershipRow).where(
                MembershipRow.user_id == user.id,
                MembershipRow.workspace_id == workspace_id,
            )
        )
        if existing is not None:
            raise DuplicateMembershipError

        membership = MembershipRow(
            id=uuid4(),
            user_id=user.id,
            workspace_id=workspace_id,
            role=payload.role.value,
        )
        self.session.add(membership)
        self.session.flush()
        return self._membership_read(membership, user.email)

    def list_memberships_for_user(
        self,
        current_user_id: UUID,
        workspace_id: UUID,
    ) -> list[MembershipRead] | None:
        if not self.user_has_workspace_membership(current_user_id, workspace_id):
            return None

        rows = self.session.execute(
            select(MembershipRow, UserRow.email)
            .join(UserRow, UserRow.id == MembershipRow.user_id)
            .where(MembershipRow.workspace_id == workspace_id)
            .order_by(MembershipRow.created_at)
        ).all()
        return [self._membership_read(row, email) for row, email in rows]

    def update_membership_for_user(
        self,
        current_user_id: UUID,
        workspace_id: UUID,
        membership_id: UUID,
        payload: MembershipUpdate,
    ) -> MembershipRead | None:
        current_role = self.workspace_role_for_user(current_user_id, workspace_id)
        if current_role is None:
            return None
        if current_role != "owner":
            raise PermissionDeniedError

        row_and_email = self._membership_row_with_email(workspace_id, membership_id)
        if row_and_email is None:
            return None

        row, email = row_and_email
        if row.role == "owner" and payload.role.value != "owner":
            self._ensure_not_last_owner(workspace_id)

        row.role = payload.role.value
        self.session.flush()
        return self._membership_read(row, email)

    def delete_membership_for_user(
        self,
        current_user_id: UUID,
        workspace_id: UUID,
        membership_id: UUID,
    ) -> bool | None:
        current_role = self.workspace_role_for_user(current_user_id, workspace_id)
        if current_role is None:
            return None

        row_and_email = self._membership_row_with_email(workspace_id, membership_id)
        if row_and_email is None:
            return None

        row, _email = row_and_email
        if current_role == "member":
            raise PermissionDeniedError
        if current_role == "admin" and row.role != "member":
            raise PermissionDeniedError
        if row.role == "owner":
            self._ensure_not_last_owner(workspace_id)

        self.session.delete(row)
        self.session.flush()
        return True

    def create_workspace_project_for_user(
        self,
        user_id: UUID,
        workspace_id: UUID,
        payload: ProjectCreate,
    ) -> ProjectRead | None:
        if not self.user_has_workspace_membership(user_id, workspace_id):
            return None

        project = ProjectRow(
            id=uuid4(),
            workspace_id=workspace_id,
            name=payload.name,
        )
        self.session.add(project)
        self.session.flush()
        return self._project_read(project)

    def list_workspace_projects_for_user(
        self,
        user_id: UUID,
        workspace_id: UUID,
        page_size: int,
    ) -> list[ProjectRead] | None:
        if not self.user_has_workspace_membership(user_id, workspace_id):
            return None

        rows = self.session.scalars(
            select(ProjectRow)
            .where(ProjectRow.workspace_id == workspace_id)
            .order_by(ProjectRow.created_at)
            .limit(page_size)
        ).all()
        return [self._project_read(row) for row in rows]

    def get_workspace_project_for_user(
        self,
        user_id: UUID,
        workspace_id: UUID,
        project_id: UUID,
    ) -> ProjectRead | None:
        row = self._accessible_project_row(user_id, workspace_id, project_id)
        if row is None:
            return None
        return self._project_read(row)

    def update_workspace_project_for_user(
        self,
        user_id: UUID,
        workspace_id: UUID,
        project_id: UUID,
        payload: ProjectUpdate,
    ) -> ProjectRead | None:
        row = self._accessible_project_row(user_id, workspace_id, project_id)
        if row is None:
            return None

        row.name = payload.name
        self.session.flush()
        return self._project_read(row)

    def delete_workspace_project_for_user(
        self,
        user_id: UUID,
        workspace_id: UUID,
        project_id: UUID,
    ) -> bool | None:
        role = self.workspace_role_for_user(user_id, workspace_id)
        if role is None:
            return None

        row = self.session.scalar(
            select(ProjectRow).where(
                ProjectRow.id == project_id,
                ProjectRow.workspace_id == workspace_id,
            )
        )
        if row is None:
            return None

        if role not in {"owner", "admin"}:
            return False

        self.session.delete(row)
        self.session.flush()
        return True

    def create_workspace_task_for_user(
        self,
        user_id: UUID,
        workspace_id: UUID,
        project_id: UUID,
        payload: TaskCreate,
    ) -> TaskRead | None:
        if self._accessible_project_row(user_id, workspace_id, project_id) is None:
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

    def list_workspace_tasks_for_user(
        self,
        user_id: UUID,
        workspace_id: UUID,
        project_id: UUID,
        page_size: int,
        after_created_at: datetime | None = None,
        after_id: UUID | None = None,
    ) -> list[TaskRead] | None:
        if self._accessible_project_row(user_id, workspace_id, project_id) is None:
            return None

        statement = select(TaskRow).where(TaskRow.project_id == project_id)

        if after_created_at is not None and after_id is not None:
            statement = statement.where(
                tuple_(TaskRow.created_at, TaskRow.id) > (after_created_at, after_id)
            )

        statement = statement.order_by(TaskRow.created_at, TaskRow.id).limit(page_size)

        rows = self.session.scalars(statement).all()
        return [self._task_read(row) for row in rows]

    def get_workspace_task_for_user(
        self,
        user_id: UUID,
        workspace_id: UUID,
        project_id: UUID,
        task_id: UUID,
    ) -> TaskRead | None:
        row = self._accessible_task_row(user_id, workspace_id, project_id, task_id)
        if row is None:
            return None
        return self._task_read(row)

    def update_workspace_task_for_user(
        self,
        user_id: UUID,
        workspace_id: UUID,
        project_id: UUID,
        task_id: UUID,
        payload: TaskUpdate,
    ) -> TaskRead | None:
        if (
            self._accessible_task_row(user_id, workspace_id, project_id, task_id)
            is None
        ):
            return None

        values: dict[str, object] = {"version": TaskRow.version + 1}
        if payload.title is not None:
            values["title"] = payload.title
        if payload.status is not None:
            values["status"] = payload.status.value

        row = self.session.scalar(
            update(TaskRow)
            .where(
                TaskRow.id == task_id,
                TaskRow.project_id == project_id,
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

    def delete_workspace_task_for_user(
        self,
        user_id: UUID,
        workspace_id: UUID,
        project_id: UUID,
        task_id: UUID,
    ) -> bool:
        row = self._accessible_task_row(user_id, workspace_id, project_id, task_id)
        if row is None:
            return False

        self.session.delete(row)
        self.session.flush()
        return True

    def user_has_workspace_membership(self, user_id: UUID, workspace_id: UUID) -> bool:
        return self.workspace_role_for_user(user_id, workspace_id) is not None

    def workspace_role_for_user(self, user_id: UUID, workspace_id: UUID) -> str | None:
        return self.session.scalar(
            select(MembershipRow.role).where(
                MembershipRow.user_id == user_id,
                MembershipRow.workspace_id == workspace_id,
            )
        )

    def _membership_row_with_email(
        self,
        workspace_id: UUID,
        membership_id: UUID,
    ) -> tuple[MembershipRow, str] | None:
        result = self.session.execute(
            select(MembershipRow, UserRow.email)
            .join(UserRow, UserRow.id == MembershipRow.user_id)
            .where(
                MembershipRow.id == membership_id,
                MembershipRow.workspace_id == workspace_id,
            )
        ).one_or_none()
        if result is None:
            return None
        row, email = result
        return row, email

    def _ensure_not_last_owner(self, workspace_id: UUID) -> None:
        owner_count = self.session.scalar(
            select(func.count())
            .select_from(MembershipRow)
            .where(
                MembershipRow.workspace_id == workspace_id,
                MembershipRow.role == "owner",
            )
        )
        if owner_count == 1:
            raise LastOwnerError

    def _accessible_project_row(
        self,
        user_id: UUID,
        workspace_id: UUID,
        project_id: UUID,
    ) -> ProjectRow | None:
        return self.session.scalar(
            select(ProjectRow)
            .join(MembershipRow, MembershipRow.workspace_id == ProjectRow.workspace_id)
            .where(
                ProjectRow.id == project_id,
                ProjectRow.workspace_id == workspace_id,
                MembershipRow.user_id == user_id,
            )
        )

    def _accessible_task_row(
        self,
        user_id: UUID,
        workspace_id: UUID,
        project_id: UUID,
        task_id: UUID,
    ) -> TaskRow | None:
        return self.session.scalar(
            select(TaskRow)
            .join(ProjectRow, ProjectRow.id == TaskRow.project_id)
            .join(MembershipRow, MembershipRow.workspace_id == ProjectRow.workspace_id)
            .where(
                TaskRow.id == task_id,
                TaskRow.project_id == project_id,
                ProjectRow.id == project_id,
                ProjectRow.workspace_id == workspace_id,
                MembershipRow.user_id == user_id,
            )
        )

    @staticmethod
    def _workspace_read(row: WorkspaceRow) -> WorkspaceRead:
        return WorkspaceRead(id=row.id, name=row.name, created_at=row.created_at)

    @staticmethod
    def _membership_read(row: MembershipRow, email: str) -> MembershipRead:
        return MembershipRead(
            id=row.id,
            user_id=row.user_id,
            workspace_id=row.workspace_id,
            email=email,
            role=row.role,
            created_at=row.created_at,
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
