"""Project tracker schemas."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.project import ProjectStatus
from app.models.roadmap import Priority


class ProjectMilestoneRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    title: str
    description: str | None = None
    is_completed: bool
    completed_at: datetime | None = None
    due_date: date | None = None
    order_index: int


class ProjectMilestoneCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=240)
    description: str | None = Field(default=None, max_length=4000)
    due_date: date | None = None
    order_index: int | None = None


class ProjectMilestoneUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=240)
    description: str | None = Field(default=None, max_length=4000)
    due_date: date | None = None
    is_completed: bool | None = None
    order_index: int | None = None


class ProjectChecklistItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    title: str
    is_done: bool
    order_index: int


class ProjectChecklistItemCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=240)
    is_done: bool = False


class ProjectChecklistItemUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=240)
    is_done: bool | None = None


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str
    required_skills: list[str] = Field(default_factory=list)
    status: ProjectStatus
    priority: Priority
    start_date: date | None = None
    target_date: date | None = None
    repo_url: str | None = None
    demo_url: str | None = None
    notes: str | None = None
    order_index: int
    created_at: datetime
    updated_at: datetime
    milestones: list[ProjectMilestoneRead] = Field(default_factory=list)
    checklist_items: list[ProjectChecklistItemRead] = Field(default_factory=list)
    milestone_count: int = 0
    completed_milestones: int = 0
    completion_percentage: float = 0.0
    checklist_count: int = 0
    completed_checklist_items: int = 0
    checklist_percentage: float = 0.0
    days_remaining: int | None = None


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=8000)
    required_skills: list[str] = Field(default_factory=list)
    status: ProjectStatus = ProjectStatus.NOT_STARTED
    priority: Priority = Priority.MEDIUM
    start_date: date | None = None
    target_date: date | None = None
    repo_url: str | None = Field(default=None, max_length=512)
    demo_url: str | None = Field(default=None, max_length=512)
    notes: str | None = Field(default=None, max_length=8000)

    @field_validator("repo_url", "demo_url")
    @classmethod
    def _validate_url(cls, value: str | None) -> str | None:
        if value in (None, ""):
            return None
        cleaned = value.strip()
        if not cleaned.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return cleaned


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=8000)
    required_skills: list[str] | None = None
    status: ProjectStatus | None = None
    priority: Priority | None = None
    start_date: date | None = None
    target_date: date | None = None
    repo_url: str | None = Field(default=None, max_length=512)
    demo_url: str | None = Field(default=None, max_length=512)
    notes: str | None = Field(default=None, max_length=8000)

    @field_validator("repo_url", "demo_url")
    @classmethod
    def _validate_url(cls, value: str | None) -> str | None:
        if value in (None, ""):
            return None
        cleaned = value.strip()
        if not cleaned.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return cleaned


class ProjectSummary(BaseModel):
    total: int = 0
    not_started: int = 0
    in_progress: int = 0
    completed: int = 0
    average_completion: float = 0.0
