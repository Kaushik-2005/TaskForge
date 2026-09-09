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


class TaskCreate(StrictModel):
    title: str = Field(min_length=1, max_length=200)
    status: TaskStatus = TaskStatus.todo


class TaskUpdate(StrictModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    status: TaskStatus | None = None

    @model_validator(mode="after")
    def require_valid_change(self) -> "TaskUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        if "title" in self.model_fields_set and self.title is None:
            raise ValueError("Task title cannot be null")
        return self


class TaskRead(BaseModel):
    id: UUID
    project_id: UUID
    title: str
    status: TaskStatus
    created_at: datetime
