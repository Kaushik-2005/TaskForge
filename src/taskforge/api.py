from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status

from taskforge.models import (
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
    TaskCreate,
    TaskRead,
    TaskUpdate,
)
from taskforge.store import InMemoryStore, InvalidStateTransitionError

router = APIRouter(prefix="/api/v1")
PageSize = Annotated[int, Query(ge=1, le=100)]


def get_store(request: Request) -> InMemoryStore:
    return request.app.state.store


StoreDep = Annotated[InMemoryStore, Depends(get_store)]


def api_error(status_code: int, code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail={"code": code, "message": message},
    )


def not_found(message: str) -> HTTPException:
    return api_error(status.HTTP_404_NOT_FOUND, "not_found", message)


@router.post(
    "/projects",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    payload: ProjectCreate,
    response: Response,
    store: StoreDep,
) -> ProjectRead:
    project = store.create_project(payload)
    response.headers["Location"] = f"/api/v1/projects/{project.id}"
    return project


@router.get("/projects", response_model=list[ProjectRead])
def list_projects(
    store: StoreDep,
    page_size: PageSize = 20,
) -> list[ProjectRead]:
    return store.list_projects(page_size)


@router.get("/projects/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: UUID,
    store: StoreDep,
) -> ProjectRead:
    project = store.get_project(project_id)
    if project is None:
        raise not_found("Project not found")
    return project


@router.patch("/projects/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: UUID,
    payload: ProjectUpdate,
    store: StoreDep,
) -> ProjectRead:
    project = store.update_project(project_id, payload)
    if project is None:
        raise not_found("Project not found")
    return project


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: UUID,
    store: StoreDep,
) -> Response:
    if not store.delete_project(project_id):
        raise not_found("Project not found")
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
    store: StoreDep,
) -> TaskRead:
    task = store.create_task(project_id, payload)
    if task is None:
        raise not_found("Project not found")
    response.headers["Location"] = f"/api/v1/projects/{project_id}/tasks/{task.id}"
    return task


@router.get("/projects/{project_id}/tasks", response_model=list[TaskRead])
def list_tasks(
    project_id: UUID,
    store: StoreDep,
    page_size: PageSize = 20,
) -> list[TaskRead]:
    tasks = store.list_tasks(project_id, page_size)
    if tasks is None:
        raise not_found("Project not found")
    return tasks


@router.get("/projects/{project_id}/tasks/{task_id}", response_model=TaskRead)
def get_task(
    project_id: UUID,
    task_id: UUID,
    store: StoreDep,
) -> TaskRead:
    if store.get_project(project_id) is None:
        raise not_found("Project not found")
    task = store.get_task(project_id, task_id)
    if task is None:
        raise not_found("Task not found")
    return task


@router.patch("/projects/{project_id}/tasks/{task_id}", response_model=TaskRead)
def update_task(
    project_id: UUID,
    task_id: UUID,
    payload: TaskUpdate,
    store: StoreDep,
) -> TaskRead:
    if store.get_project(project_id) is None:
        raise not_found("Project not found")
    try:
        task = store.update_task(project_id, task_id, payload)
    except InvalidStateTransitionError as exc:
        raise api_error(
            status.HTTP_409_CONFLICT,
            "invalid_state_transition",
            "Task status cannot change directly from todo to done",
        ) from exc
    if task is None:
        raise not_found("Task not found")
    return task


@router.delete(
    "/projects/{project_id}/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task(
    project_id: UUID,
    task_id: UUID,
    store: StoreDep,
) -> Response:
    if store.get_project(project_id) is None:
        raise not_found("Project not found")
    if not store.delete_task(project_id, task_id):
        raise not_found("Task not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
