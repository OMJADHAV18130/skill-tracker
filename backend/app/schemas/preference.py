"""User preference + export/import schemas."""

from __future__ import annotations

import uuid
from datetime import date, datetime, time
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.preference import MAX_DAILY_GOAL, MIN_DAILY_GOAL, Theme


class PreferenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    daily_goal_minutes: int
    roadmap_start_date: date
    theme: Theme
    reminders_enabled: bool
    reminder_time: time
    timezone: str
    phase_durations: dict[str, int] = Field(default_factory=dict)
    sidebar_collapsed: bool
    dsa_paused: bool = False
    dsa_paused_at: datetime | None = None
    dsa_paused_until: date | None = None


class PreferenceUpdate(BaseModel):
    daily_goal_minutes: int | None = Field(default=None, ge=MIN_DAILY_GOAL, le=MAX_DAILY_GOAL)
    roadmap_start_date: date | None = None
    theme: Theme | None = None
    reminders_enabled: bool | None = None
    reminder_time: time | None = None
    timezone: str | None = Field(default=None, max_length=64)
    phase_durations: dict[str, int] | None = None
    sidebar_collapsed: bool | None = None

    @field_validator("phase_durations")
    @classmethod
    def _validate_phase_durations(cls, value: dict[str, int] | None) -> dict[str, int] | None:
        if value is None:
            return value
        for _key, months in value.items():
            if not 1 <= months <= 12:
                raise ValueError("Phase duration must be between 1 and 12 months")
        return value


class ExportPayload(BaseModel):
    """Full export of the user's learning progress."""

    schema_version: str = "1.0"
    exported_at: datetime
    user: dict[str, Any] = Field(default_factory=dict)
    preferences: dict[str, Any] = Field(default_factory=dict)
    topic_progress: list[dict[str, Any]] = Field(default_factory=list)
    topic_notes: list[dict[str, Any]] = Field(default_factory=list)
    topic_checklist: list[dict[str, Any]] = Field(default_factory=list)
    daily_tasks: list[dict[str, Any]] = Field(default_factory=list)
    study_sessions: list[dict[str, Any]] = Field(default_factory=list)
    projects: list[dict[str, Any]] = Field(default_factory=list)
    project_milestones: list[dict[str, Any]] = Field(default_factory=list)
    project_checklist: list[dict[str, Any]] = Field(default_factory=list)
    resource_bookmarks: list[dict[str, Any]] = Field(default_factory=list)


class DsaPauseRequest(BaseModel):
    """Pause the parallel DSA track, optionally until a specific date."""

    resume_on: date | None = Field(
        default=None,
        description="Automatically resume on this date. Omit to pause indefinitely.",
    )

    @field_validator("resume_on")
    @classmethod
    def _validate_resume_on(cls, value: date | None) -> date | None:
        if value is not None and value <= date.today():
            raise ValueError("The resume date must be in the future")
        return value


class ImportPreview(BaseModel):
    valid: bool
    schema_version: str | None = None
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    counts: dict[str, int] = Field(default_factory=dict)


class ImportRequest(BaseModel):
    payload: ExportPayload
    confirm: bool = Field(
        default=False,
        description="Must be true - the client has confirmed the overwrite with the user",
    )
    mode: str = Field(default="replace", pattern="^(replace|merge)$")
