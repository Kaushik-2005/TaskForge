from uuid import UUID

from taskforge.authorization_repository import AuthorizationRepository
from taskforge.errors import (
    InvalidStateTransitionError,
    PermissionDeniedError,
    TaskNotFoundError,
    WorkspaceNotFoundError,
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
    UserRead,
    WorkspaceCreate,
    WorkspaceRead,
)


class AuthorizationService:
    def __init__(self, repository: AuthorizationRepository) -> None:
        self.repository = repository

    def create_workspace(
        self,
        current_user: UserRead,
        payload: WorkspaceCreate,
    ) -> WorkspaceRead:
        return self.repository.create_workspace_for_owner(
            user_id=current_user.id,
            payload=payload,
        )

    def create_membership(
        self,
        current_user: UserRead,
        workspace_id: UUID,
        payload: MembershipCreate,
    ) -> MembershipRead:
        membership = self.repository.create_membership_for_user(
            current_user_id=current_user.id,
            workspace_id=workspace_id,
            payload=payload,
        )
        if membership is None:
            raise WorkspaceNotFoundError
        return membership

    def list_memberships(
        self,
        current_user: UserRead,
        workspace_id: UUID,
    ) -> list[MembershipRead]:
        memberships = self.repository.list_memberships_for_user(
            current_user_id=current_user.id,
            workspace_id=workspace_id,
        )
        if memberships is None:
            raise WorkspaceNotFoundError
        return memberships

    def update_membership(
        self,
        current_user: UserRead,
        workspace_id: UUID,
        membership_id: UUID,
        payload: MembershipUpdate,
    ) -> MembershipRead:
        membership = self.repository.update_membership_for_user(
            current_user_id=current_user.id,
            workspace_id=workspace_id,
            membership_id=membership_id,
            payload=payload,
        )
        if membership is None:
            raise WorkspaceNotFoundError
        return membership

    def delete_membership(
        self,
        current_user: UserRead,
        workspace_id: UUID,
        membership_id: UUID,
    ) -> None:
        deleted = self.repository.delete_membership_for_user(
            current_user_id=current_user.id,
            workspace_id=workspace_id,
            membership_id=membership_id,
        )
        if deleted is None:
            raise WorkspaceNotFoundError
        if deleted is False:
            raise PermissionDeniedError

    def create_workspace_project(
        self,
        current_user: UserRead,
        workspace_id: UUID,
        payload: ProjectCreate,
    ) -> ProjectRead:
        project = self.repository.create_workspace_project_for_user(
            user_id=current_user.id,
            workspace_id=workspace_id,
            payload=payload,
        )
        if project is None:
            raise WorkspaceNotFoundError
        return project

    def list_workspace_projects(
        self,
        current_user: UserRead,
        workspace_id: UUID,
        page_size: int,
    ) -> list[ProjectRead]:
        projects = self.repository.list_workspace_projects_for_user(
            user_id=current_user.id,
            workspace_id=workspace_id,
            page_size=page_size,
        )
        if projects is None:
            raise WorkspaceNotFoundError
        return projects

    def get_workspace_project(
        self,
        current_user: UserRead,
        workspace_id: UUID,
        project_id: UUID,
    ) -> ProjectRead:
        project = self.repository.get_workspace_project_for_user(
            user_id=current_user.id,
            workspace_id=workspace_id,
            project_id=project_id,
        )
        if project is None:
            raise WorkspaceNotFoundError
        return project

    def update_workspace_project(
        self,
        current_user: UserRead,
        workspace_id: UUID,
        project_id: UUID,
        payload: ProjectUpdate,
    ) -> ProjectRead:
        project = self.repository.update_workspace_project_for_user(
            user_id=current_user.id,
            workspace_id=workspace_id,
            project_id=project_id,
            payload=payload,
        )
        if project is None:
            raise WorkspaceNotFoundError
        return project

    def delete_workspace_project(
        self,
        current_user: UserRead,
        workspace_id: UUID,
        project_id: UUID,
    ) -> None:
        deleted = self.repository.delete_workspace_project_for_user(
            user_id=current_user.id,
            workspace_id=workspace_id,
            project_id=project_id,
        )
        if deleted is None:
            raise WorkspaceNotFoundError
        if deleted is False:
            raise PermissionDeniedError

    def create_workspace_task(
        self,
        current_user: UserRead,
        workspace_id: UUID,
        project_id: UUID,
        payload: TaskCreate,
    ) -> TaskRead:
        task = self.repository.create_workspace_task_for_user(
            user_id=current_user.id,
            workspace_id=workspace_id,
            project_id=project_id,
            payload=payload,
        )
        if task is None:
            raise WorkspaceNotFoundError
        return task

    def list_workspace_tasks(
        self,
        current_user: UserRead,
        workspace_id: UUID,
        project_id: UUID,
        page_size: int,
    ) -> list[TaskRead]:
        tasks = self.repository.list_workspace_tasks_for_user(
            user_id=current_user.id,
            workspace_id=workspace_id,
            project_id=project_id,
            page_size=page_size,
        )
        if tasks is None:
            raise WorkspaceNotFoundError
        return tasks

    def get_workspace_task(
        self,
        current_user: UserRead,
        workspace_id: UUID,
        project_id: UUID,
        task_id: UUID,
    ) -> TaskRead:
        task = self.repository.get_workspace_task_for_user(
            user_id=current_user.id,
            workspace_id=workspace_id,
            project_id=project_id,
            task_id=task_id,
        )
        if task is None:
            raise TaskNotFoundError
        return task

    def update_workspace_task(
        self,
        current_user: UserRead,
        workspace_id: UUID,
        project_id: UUID,
        task_id: UUID,
        payload: TaskUpdate,
    ) -> TaskRead:
        task = self.get_workspace_task(current_user, workspace_id, project_id, task_id)
        if task.status == TaskStatus.todo and payload.status == TaskStatus.done:
            raise InvalidStateTransitionError

        updated = self.repository.update_workspace_task_for_user(
            user_id=current_user.id,
            workspace_id=workspace_id,
            project_id=project_id,
            task_id=task_id,
            payload=payload,
        )
        if updated is None:
            raise TaskNotFoundError
        return updated

    def delete_workspace_task(
        self,
        current_user: UserRead,
        workspace_id: UUID,
        project_id: UUID,
        task_id: UUID,
    ) -> None:
        if not self.repository.delete_workspace_task_for_user(
            user_id=current_user.id,
            workspace_id=workspace_id,
            project_id=project_id,
            task_id=task_id,
        ):
            raise TaskNotFoundError
