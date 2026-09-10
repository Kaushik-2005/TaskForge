from collections.abc import Generator
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status

from taskforge.errors import (
    InvalidStateTransitionError,
    ProjectNotFoundError,
    TaskForgeError,
    TaskNotFoundError,
)
from taskforge.models import (
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
    TaskCreate,
    TaskRead,
    TaskUpdate,
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


ServiceDep = Annotated[TaskForgeService, Depends(get_service)]


def api_error(status_code: int, code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail={"code": code, "message": message},
    )


def map_service_error(error: TaskForgeError) -> HTTPException:
    if isinstance(error, ProjectNotFoundError | TaskNotFoundError):
        return api_error(status.HTTP_404_NOT_FOUND, error.code, error.message)
    if isinstance(error, InvalidStateTransitionError):
        return api_error(status.HTTP_409_CONFLICT, error.code, error.message)
    return api_error(status.HTTP_500_INTERNAL_SERVER_ERROR, error.code, error.message)


@router.post(
    "/projects",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    payload: ProjectCreate,
    response: Response,
    service: ServiceDep,
) -> ProjectRead:
    project = service.create_project(payload)
    response.headers["Location"] = f"/api/v1/projects/{project.id}"
    return project


@router.get("/projects", response_model=list[ProjectRead])
def list_projects(
    service: ServiceDep,
    page_size: PageSize = 20,
) -> list[ProjectRead]:
    return service.list_projects(page_size)


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
) -> ProjectRead:
    try:
        return service.update_project(project_id, payload)
    except TaskForgeError as exc:
        raise map_service_error(exc) from exc


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: UUID,
    service: ServiceDep,
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
) -> list[TaskRead]:
    try:
        return service.list_tasks(project_id, page_size)
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
) -> Response:
    try:
        service.delete_task(project_id, task_id)
    except TaskForgeError as exc:
        raise map_service_error(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
