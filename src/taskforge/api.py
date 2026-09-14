from collections.abc import Generator
from datetime import datetime, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status

from taskforge.auth_repository import AuthRepository
from taskforge.auth_service import AuthService
from taskforge.authorization_repository import AuthorizationRepository
from taskforge.authorization_service import AuthorizationService
from taskforge.errors import (
    AuthError,
    CsrfError,
    DuplicateMembershipError,
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    InvalidStateTransitionError,
    LastOwnerError,
    PermissionDeniedError,
    ProjectNotFoundError,
    StaleTaskVersionError,
    TaskForgeError,
    TaskNotFoundError,
    UnauthenticatedError,
    UserNotFoundError,
    WorkspaceNotFoundError,
)
from taskforge.models import (
    AuthSessionRead,
    MembershipCreate,
    MembershipRead,
    MembershipUpdate,
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
    TaskCreate,
    TaskRead,
    TaskUpdate,
    UserLogin,
    UserRead,
    UserRegister,
    WorkspaceCreate,
    WorkspaceRead,
)
from taskforge.repositories import PostgresStore
from taskforge.services import TaskForgeService

router = APIRouter(prefix="/api/v1")
PageSize = Annotated[int, Query(ge=1, le=100)]


def get_service(request: Request) -> Generator[TaskForgeService]:
    session_factory = getattr(request.app.state, "session_factory", None)
    if session_factory is None:
        yield request.app.state.service
        return

    with session_factory() as session:
        service = TaskForgeService(PostgresStore(session, request.app.state.settings))
        try:
            yield service
            session.commit()
        except Exception:
            session.rollback()
            raise


def get_auth_service(request: Request) -> Generator[AuthService]:
    session_factory = getattr(request.app.state, "session_factory", None)
    if session_factory is None:
        raise api_error(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "auth_unavailable",
            "Authentication requires PostgreSQL storage",
        )

    settings = request.app.state.settings
    with session_factory() as session:
        service = AuthService(
            AuthRepository(session),
            session_ttl=timedelta(minutes=settings.session_ttl_minutes),
        )
        try:
            yield service
            session.commit()
        except Exception:
            session.rollback()
            raise


def get_authorization_service(request: Request) -> Generator[AuthorizationService]:
    session_factory = getattr(request.app.state, "session_factory", None)
    if session_factory is None:
        raise api_error(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "authorization_unavailable",
            "Authorization requires PostgreSQL storage",
        )

    with session_factory() as session:
        service = AuthorizationService(AuthorizationRepository(session))
        try:
            yield service
            session.commit()
        except Exception:
            session.rollback()
            raise


ServiceDep = Annotated[TaskForgeService, Depends(get_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
AuthorizationServiceDep = Annotated[
    AuthorizationService,
    Depends(get_authorization_service),
]


def api_error(status_code: int, code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail={"code": code, "message": message},
    )


def map_service_error(error: TaskForgeError) -> HTTPException:
    if isinstance(
        error,
        ProjectNotFoundError
        | TaskNotFoundError
        | UserNotFoundError
        | WorkspaceNotFoundError,
    ):
        return api_error(status.HTTP_404_NOT_FOUND, error.code, error.message)
    if isinstance(error, DuplicateMembershipError | LastOwnerError):
        return api_error(status.HTTP_409_CONFLICT, error.code, error.message)
    if isinstance(error, PermissionDeniedError):
        return api_error(status.HTTP_403_FORBIDDEN, error.code, error.message)
    if isinstance(error, InvalidStateTransitionError | StaleTaskVersionError):
        return api_error(status.HTTP_409_CONFLICT, error.code, error.message)
    return api_error(status.HTTP_500_INTERNAL_SERVER_ERROR, error.code, error.message)


def map_auth_error(error: AuthError) -> HTTPException:
    if isinstance(error, EmailAlreadyRegisteredError):
        return api_error(status.HTTP_409_CONFLICT, error.code, error.message)
    if isinstance(error, InvalidCredentialsError | UnauthenticatedError):
        return api_error(status.HTTP_401_UNAUTHORIZED, error.code, error.message)
    if isinstance(error, CsrfError):
        return api_error(status.HTTP_403_FORBIDDEN, error.code, error.message)
    return api_error(status.HTTP_500_INTERNAL_SERVER_ERROR, error.code, error.message)


def set_session_cookie(
    request: Request, response: Response, session_token: str
) -> None:
    settings = request.app.state.settings
    response.set_cookie(
        key=settings.session_cookie_name,
        value=session_token,
        max_age=settings.session_ttl_minutes * 60,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="lax",
        path="/",
    )


def clear_session_cookie(request: Request, response: Response) -> None:
    settings = request.app.state.settings
    response.delete_cookie(
        key=settings.session_cookie_name,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="lax",
        path="/",
    )


def require_csrf_for_cookie_auth(request: Request) -> None:
    settings = request.app.state.settings
    session_token = request.cookies.get(settings.session_cookie_name)
    if session_token is None:
        return

    csrf_token = request.headers.get(settings.csrf_header_name)
    session_factory = getattr(request.app.state, "session_factory", None)
    if session_factory is None:
        raise map_auth_error(CsrfError()) from None

    with session_factory() as session:
        service = AuthService(
            AuthRepository(session),
            session_ttl=timedelta(minutes=settings.session_ttl_minutes),
        )
        if not service.csrf_token_is_valid(session_token, csrf_token):
            raise map_auth_error(CsrfError()) from None


CsrfDep = Annotated[None, Depends(require_csrf_for_cookie_auth)]


def get_current_user(request: Request) -> Generator[UserRead]:
    session_factory = getattr(request.app.state, "session_factory", None)
    if session_factory is None:
        raise map_auth_error(UnauthenticatedError()) from None

    settings = request.app.state.settings
    session_token = request.cookies.get(settings.session_cookie_name)

    with session_factory() as session:
        auth = AuthService(
            AuthRepository(session),
            session_ttl=timedelta(minutes=settings.session_ttl_minutes),
        )
        try:
            yield auth.current_user(session_token)
        except AuthError as exc:
            raise map_auth_error(exc) from exc


CurrentUserDep = Annotated[UserRead, Depends(get_current_user)]


@router.post(
    "/auth/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def register_user(payload: UserRegister, auth: AuthServiceDep) -> UserRead:
    try:
        return auth.register(payload.email, payload.password)
    except AuthError as exc:
        raise map_auth_error(exc) from exc


@router.post("/auth/login", response_model=AuthSessionRead)
def login_user(
    payload: UserLogin,
    request: Request,
    response: Response,
    auth: AuthServiceDep,
) -> AuthSessionRead:
    try:
        session = auth.login(payload.email, payload.password)
    except AuthError as exc:
        raise map_auth_error(exc) from exc
    set_session_cookie(request, response, session.session_token)
    return AuthSessionRead(user=session.user, csrf_token=session.csrf_token)


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout_user(
    request: Request,
    response: Response,
    _csrf: CsrfDep,
    auth: AuthServiceDep,
) -> Response:
    settings = request.app.state.settings
    auth.logout(request.cookies.get(settings.session_cookie_name))
    clear_session_cookie(request, response)
    return Response(status_code=status.HTTP_204_NO_CONTENT, headers=response.headers)


@router.get("/auth/me", response_model=UserRead)
def read_current_user(request: Request, auth: AuthServiceDep) -> UserRead:
    settings = request.app.state.settings
    try:
        return auth.current_user(request.cookies.get(settings.session_cookie_name))
    except AuthError as exc:
        raise map_auth_error(exc) from exc


@router.post(
    "/workspaces",
    response_model=WorkspaceRead,
    status_code=status.HTTP_201_CREATED,
)
def create_workspace(
    payload: WorkspaceCreate,
    current_user: CurrentUserDep,
    authorization: AuthorizationServiceDep,
    _csrf: CsrfDep,
) -> WorkspaceRead:
    return authorization.create_workspace(current_user, payload)


@router.post(
    "/workspaces/{workspace_id}/memberships",
    response_model=MembershipRead,
    status_code=status.HTTP_201_CREATED,
)
def create_membership(
    workspace_id: UUID,
    payload: MembershipCreate,
    current_user: CurrentUserDep,
    authorization: AuthorizationServiceDep,
    _csrf: CsrfDep,
) -> MembershipRead:
    try:
        return authorization.create_membership(current_user, workspace_id, payload)
    except TaskForgeError as exc:
        raise map_service_error(exc) from exc


@router.get(
    "/workspaces/{workspace_id}/memberships",
    response_model=list[MembershipRead],
)
def list_memberships(
    workspace_id: UUID,
    current_user: CurrentUserDep,
    authorization: AuthorizationServiceDep,
) -> list[MembershipRead]:
    try:
        return authorization.list_memberships(current_user, workspace_id)
    except TaskForgeError as exc:
        raise map_service_error(exc) from exc


@router.patch(
    "/workspaces/{workspace_id}/memberships/{membership_id}",
    response_model=MembershipRead,
)
def update_membership(
    workspace_id: UUID,
    membership_id: UUID,
    payload: MembershipUpdate,
    current_user: CurrentUserDep,
    authorization: AuthorizationServiceDep,
    _csrf: CsrfDep,
) -> MembershipRead:
    try:
        return authorization.update_membership(
            current_user,
            workspace_id,
            membership_id,
            payload,
        )
    except TaskForgeError as exc:
        raise map_service_error(exc) from exc


@router.delete(
    "/workspaces/{workspace_id}/memberships/{membership_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_membership(
    workspace_id: UUID,
    membership_id: UUID,
    current_user: CurrentUserDep,
    authorization: AuthorizationServiceDep,
    _csrf: CsrfDep,
) -> Response:
    try:
        authorization.delete_membership(current_user, workspace_id, membership_id)
    except TaskForgeError as exc:
        raise map_service_error(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/workspaces/{workspace_id}/projects",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
)
def create_workspace_project(
    workspace_id: UUID,
    payload: ProjectCreate,
    response: Response,
    current_user: CurrentUserDep,
    authorization: AuthorizationServiceDep,
    _csrf: CsrfDep,
) -> ProjectRead:
    try:
        project = authorization.create_workspace_project(
            current_user,
            workspace_id,
            payload,
        )
    except TaskForgeError as exc:
        raise map_service_error(exc) from exc
    response.headers["Location"] = (
        f"/api/v1/workspaces/{workspace_id}/projects/{project.id}"
    )
    return project


@router.get(
    "/workspaces/{workspace_id}/projects",
    response_model=list[ProjectRead],
)
def list_workspace_projects(
    workspace_id: UUID,
    current_user: CurrentUserDep,
    authorization: AuthorizationServiceDep,
    page_size: PageSize = 20,
) -> list[ProjectRead]:
    try:
        return authorization.list_workspace_projects(
            current_user,
            workspace_id,
            page_size,
        )
    except TaskForgeError as exc:
        raise map_service_error(exc) from exc


@router.get(
    "/workspaces/{workspace_id}/projects/{project_id}",
    response_model=ProjectRead,
)
def get_workspace_project(
    workspace_id: UUID,
    project_id: UUID,
    current_user: CurrentUserDep,
    authorization: AuthorizationServiceDep,
) -> ProjectRead:
    try:
        return authorization.get_workspace_project(
            current_user,
            workspace_id,
            project_id,
        )
    except TaskForgeError as exc:
        raise map_service_error(exc) from exc


@router.patch(
    "/workspaces/{workspace_id}/projects/{project_id}",
    response_model=ProjectRead,
)
def update_workspace_project(
    workspace_id: UUID,
    project_id: UUID,
    payload: ProjectUpdate,
    current_user: CurrentUserDep,
    authorization: AuthorizationServiceDep,
    _csrf: CsrfDep,
) -> ProjectRead:
    try:
        return authorization.update_workspace_project(
            current_user,
            workspace_id,
            project_id,
            payload,
        )
    except TaskForgeError as exc:
        raise map_service_error(exc) from exc


@router.delete(
    "/workspaces/{workspace_id}/projects/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_workspace_project(
    workspace_id: UUID,
    project_id: UUID,
    current_user: CurrentUserDep,
    authorization: AuthorizationServiceDep,
    _csrf: CsrfDep,
) -> Response:
    try:
        authorization.delete_workspace_project(
            current_user,
            workspace_id,
            project_id,
        )
    except TaskForgeError as exc:
        raise map_service_error(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/workspaces/{workspace_id}/projects/{project_id}/tasks",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
)
def create_workspace_task(
    workspace_id: UUID,
    project_id: UUID,
    payload: TaskCreate,
    response: Response,
    current_user: CurrentUserDep,
    authorization: AuthorizationServiceDep,
    _csrf: CsrfDep,
) -> TaskRead:
    try:
        task = authorization.create_workspace_task(
            current_user,
            workspace_id,
            project_id,
            payload,
        )
    except TaskForgeError as exc:
        raise map_service_error(exc) from exc
    response.headers["Location"] = (
        f"/api/v1/workspaces/{workspace_id}/projects/{project_id}/tasks/{task.id}"
    )
    return task


@router.get(
    "/workspaces/{workspace_id}/projects/{project_id}/tasks",
    response_model=list[TaskRead],
)
def list_workspace_tasks(
    workspace_id: UUID,
    project_id: UUID,
    current_user: CurrentUserDep,
    authorization: AuthorizationServiceDep,
    page_size: PageSize = 20,
    after_created_at: datetime | None = None,
    after_id: UUID | None = None,
) -> list[TaskRead]:
    if (after_created_at is None) != (after_id is None):
        raise api_error(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "validation_error",
            "after_created_at and after_id must be supplied together",
        )

    try:
        return authorization.list_workspace_tasks(
            current_user,
            workspace_id,
            project_id,
            page_size,
            after_created_at=after_created_at,
            after_id=after_id,
        )
    except TaskForgeError as exc:
        raise map_service_error(exc) from exc


@router.get(
    "/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}",
    response_model=TaskRead,
)
def get_workspace_task(
    workspace_id: UUID,
    project_id: UUID,
    task_id: UUID,
    current_user: CurrentUserDep,
    authorization: AuthorizationServiceDep,
) -> TaskRead:
    try:
        return authorization.get_workspace_task(
            current_user,
            workspace_id,
            project_id,
            task_id,
        )
    except TaskForgeError as exc:
        raise map_service_error(exc) from exc


@router.patch(
    "/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}",
    response_model=TaskRead,
)
def update_workspace_task(
    workspace_id: UUID,
    project_id: UUID,
    task_id: UUID,
    payload: TaskUpdate,
    current_user: CurrentUserDep,
    authorization: AuthorizationServiceDep,
    _csrf: CsrfDep,
) -> TaskRead:
    try:
        return authorization.update_workspace_task(
            current_user,
            workspace_id,
            project_id,
            task_id,
            payload,
        )
    except TaskForgeError as exc:
        raise map_service_error(exc) from exc


@router.delete(
    "/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_workspace_task(
    workspace_id: UUID,
    project_id: UUID,
    task_id: UUID,
    current_user: CurrentUserDep,
    authorization: AuthorizationServiceDep,
    _csrf: CsrfDep,
) -> Response:
    try:
        authorization.delete_workspace_task(
            current_user,
            workspace_id,
            project_id,
            task_id,
        )
    except TaskForgeError as exc:
        raise map_service_error(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/projects",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    payload: ProjectCreate,
    response: Response,
    service: ServiceDep,
    _csrf: CsrfDep,
) -> ProjectRead:
    project = service.create_project(payload)
    response.headers["Location"] = f"/api/v1/projects/{project.id}"
    return project


@router.get("/projects", response_model=list[ProjectRead])
def list_projects(
    service: ServiceDep,
    page_size: PageSize = 20,
    name_contains: str | None = Query(
        default=None,
        min_length=1,
        max_length=120,
    ),
) -> list[ProjectRead]:
    return service.list_projects(
        page_size,
        name_contains=name_contains,
    )


@router.get("/projects/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: UUID,
    service: ServiceDep,
) -> ProjectRead:
    try:
        return service.get_project(project_id)
    except TaskForgeError as exc:
        raise map_service_error(exc) from exc


@router.patch("/projects/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: UUID,
    payload: ProjectUpdate,
    service: ServiceDep,
    _csrf: CsrfDep,
) -> ProjectRead:
    try:
        return service.update_project(project_id, payload)
    except TaskForgeError as exc:
        raise map_service_error(exc) from exc


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: UUID,
    service: ServiceDep,
    _csrf: CsrfDep,
) -> Response:
    try:
        service.delete_project(project_id)
    except TaskForgeError as exc:
        raise map_service_error(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/projects/{project_id}/tasks",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    project_id: UUID,
    payload: TaskCreate,
    response: Response,
    service: ServiceDep,
    _csrf: CsrfDep,
) -> TaskRead:
    try:
        task = service.create_task(project_id, payload)
    except TaskForgeError as exc:
        raise map_service_error(exc) from exc
    response.headers["Location"] = f"/api/v1/projects/{project_id}/tasks/{task.id}"
    return task


@router.get("/projects/{project_id}/tasks", response_model=list[TaskRead])
def list_tasks(
    project_id: UUID,
    service: ServiceDep,
    page_size: PageSize = 20,
    after_created_at: datetime | None = None,
    after_id: UUID | None = None,
) -> list[TaskRead]:
    if (after_created_at is None) != (after_id is None):
        raise api_error(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "validation_error",
            "after_created_at and after_id must be supplied together",
        )

    try:
        return service.list_tasks(
            project_id,
            page_size,
            after_created_at=after_created_at,
            after_id=after_id,
        )
    except TaskForgeError as exc:
        raise map_service_error(exc) from exc


@router.get("/projects/{project_id}/tasks/{task_id}", response_model=TaskRead)
def get_task(
    project_id: UUID,
    task_id: UUID,
    service: ServiceDep,
) -> TaskRead:
    try:
        return service.get_task(project_id, task_id)
    except TaskForgeError as exc:
        raise map_service_error(exc) from exc


@router.patch("/projects/{project_id}/tasks/{task_id}", response_model=TaskRead)
def update_task(
    project_id: UUID,
    task_id: UUID,
    payload: TaskUpdate,
    service: ServiceDep,
    _csrf: CsrfDep,
) -> TaskRead:
    try:
        return service.update_task(project_id, task_id, payload)
    except TaskForgeError as exc:
        raise map_service_error(exc) from exc


@router.delete(
    "/projects/{project_id}/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task(
    project_id: UUID,
    task_id: UUID,
    service: ServiceDep,
    _csrf: CsrfDep,
) -> Response:
    try:
        service.delete_task(project_id, task_id)
    except TaskForgeError as exc:
        raise map_service_error(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
