from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TaskStatus(StrEnum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class ProjectCreate(StrictModel):
    name: str = Field(min_length=1, max_length=120)


class ProjectUpdate(StrictModel):
    name: str = Field(min_length=1, max_length=120)


class ProjectRead(BaseModel):
    id: UUID
    name: str
    created_at: datetime


class ProjectSummaryRead(BaseModel):
    id: UUID
    workspace_id: UUID
    name: str
    task_count: int


class TaskCreate(StrictModel):
    title: str = Field(min_length=1, max_length=200)
    status: TaskStatus = TaskStatus.todo


class TaskUpdate(StrictModel):
    expected_version: int = Field(ge=1)
    title: str | None = Field(default=None, min_length=1, max_length=200)
    status: TaskStatus | None = None

    @model_validator(mode="after")
    def require_valid_change(self) -> "TaskUpdate":
        if self.title is None and self.status is None:
            raise ValueError("At least one task field must be provided")
        if "title" in self.model_fields_set and self.title is None:
            raise ValueError("Task title cannot be null")
        return self


class TaskRead(BaseModel):
    id: UUID
    project_id: UUID
    title: str
    status: TaskStatus
    version: int
    created_at: datetime


class UserRegister(StrictModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=12, max_length=128)


class UserLogin(StrictModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=128)


class UserRead(BaseModel):
    id: UUID
    email: str
    created_at: datetime


class AuthSessionRead(BaseModel):
    user: UserRead
    csrf_token: str


class WorkspaceCreate(StrictModel):
    name: str = Field(min_length=1, max_length=120)


class WorkspaceRead(BaseModel):
    id: UUID
    name: str
    created_at: datetime


class MembershipRole(StrEnum):
    owner = "owner"
    admin = "admin"
    member = "member"


class MembershipCreate(StrictModel):
    email: str = Field(min_length=3, max_length=320)
    role: MembershipRole = MembershipRole.member


class MembershipUpdate(StrictModel):
    role: MembershipRole


class MembershipRead(BaseModel):
    id: UUID
    user_id: UUID
    workspace_id: UUID
    email: str
    role: MembershipRole
    created_at: datetime
