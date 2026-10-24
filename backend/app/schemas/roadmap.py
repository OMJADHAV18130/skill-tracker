"""Roadmap schemas: phases, topics, progress, notes, checklists."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.roadmap import Priority, TopicStatus


class TopicProgressRead(BaseModel):
    status: TopicStatus = TopicStatus.NOT_STARTED
    priority: Priority = Priority.MEDIUM
    rating: int | None = Field(default=None, ge=1, le=5)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    notes: list[TopicNoteRead] = Field(default_factory=list)
    checklist: list[TopicChecklistItemRead] = Field(default_factory=list)


class TopicNoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    topic_id: uuid.UUID
    content: str
    created_at: datetime
    updated_at: datetime


class TopicNoteCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=10_000)

    @field_validator("content")
    @classmethod
    def _strip(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Note content cannot be empty")
        return cleaned


class TopicNoteUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=10_000)


class TopicChecklistItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    topic_id: uuid.UUID
    title: str
    is_done: bool
    order_index: int


class TopicChecklistItemCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=240)
    is_done: bool = False


class TopicChecklistItemUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=240)
    is_done: bool | None = None


class ResourceBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    url: str
    category: str
    description: str = ""
    is_official: bool = True


class TopicRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    phase_id: uuid.UUID
    slug: str
    title: str
    description: str
    category: str
    estimated_minutes: int
    order_index: int
    track: str = "core"
    subtopics: list[str] = Field(default_factory=list)
    is_key_topic: bool = False
    progress: TopicProgressRead = Field(default_factory=TopicProgressRead)
    resources: list[ResourceBrief] = Field(default_factory=list)


class PhaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    key: str
    title: str
    summary: str
    month_label: str
    duration_months: int
    order_index: int
    track: str = "core"
    project_brief: str | None = None
    accent: str | None = None
    topic_count: int = 0
    completed_count: int = 0
    in_progress_count: int = 0
    completion_percentage: float = 0.0
    estimated_minutes: int = 0
    status: str = "not_started"
    topics: list[TopicRead] = Field(default_factory=list)


class PhaseListResponse(BaseModel):
    items: list[PhaseRead]
    track: str = "core"
    total_topics: int = 0
    completed_topics: int = 0
    completion_percentage: float = 0.0


class TopicProgressUpdate(BaseModel):
    """Update the user's state of a topic."""

    status: TopicStatus | None = None
    priority: Priority | None = None
    rating: int | None = Field(default=None, ge=1, le=5)
    started_at: datetime | None = None
    completed_at: datetime | None = None


class TopicNavigation(BaseModel):
    previous: TopicRead | None = None
    next: TopicRead | None = None
    position: int = 0
    total: int = 0


TopicProgressRead.model_rebuild()
