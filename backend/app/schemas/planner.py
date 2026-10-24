"""Daily planner schemas."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.roadmap import Priority


class DailyTaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=240)
    description: str | None = Field(default=None, max_length=4000)
    task_date: date
    category: str = Field(default="General", min_length=1, max_length=64)
    estimated_minutes: int = Field(default=30, ge=0, le=1440)
    priority: Priority = Priority.MEDIUM
    topic_id: uuid.UUID | None = None


class DailyTaskCreate(DailyTaskBase):
    actual_minutes: int = Field(default=0, ge=0, le=1440)
    session_note: str | None = Field(default=None, max_length=2000)


class DailyTaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=240)
    description: str | None = Field(default=None, max_length=4000)
    task_date: date | None = None
    category: str | None = Field(default=None, min_length=1, max_length=64)
    estimated_minutes: int | None = Field(default=None, ge=0, le=1440)
    priority: Priority | None = None
    topic_id: uuid.UUID | None = None
    session_note: str | None = Field(default=None, max_length=2000)


class DailyTaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str | None = None
    task_date: date
    category: str
    estimated_minutes: int
    actual_minutes: int
    priority: Priority
    is_completed: bool
    completed_at: datetime | None = None
    session_note: str | None = None
    carried_from_id: uuid.UUID | None = None
    topic_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime


class TaskCompletionUpdate(BaseModel):
    is_completed: bool
    completed_at: datetime | None = None


class TaskLogTime(BaseModel):
    actual_minutes: int = Field(..., ge=0, le=1440)
    session_note: str | None = Field(default=None, max_length=2000)
    completed: bool | None = Field(
        default=None, description="Also flip the completion state of the task"
    )


class TaskCarryForward(BaseModel):
    target_date: date | None = None
    title: str | None = Field(default=None, min_length=1, max_length=240)
    delete_original: bool = Field(
        default=True, description="Remove the original task after carrying it forward"
    )


class StudySessionCreate(BaseModel):
    minutes: int = Field(..., ge=1, le=1440)
    session_date: date = Field(default_factory=date.today)
    task_id: uuid.UUID | None = None
    topic_id: uuid.UUID | None = None
    note: str | None = Field(default=None, max_length=2000)


class StudySessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    task_id: uuid.UUID | None = None
    topic_id: uuid.UUID | None = None
    session_date: date
    minutes: int
    note: str | None = None
    created_at: datetime


class DaySummary(BaseModel):
    date: date
    planned_minutes: int = 0
    completed_minutes: int = 0
    logged_minutes: int = 0
    planned_tasks: int = 0
    completed_tasks: int = 0
    goal_minutes: int = 0
    goal_percentage: float = 0.0


class DayPlanResponse(BaseModel):
    goal_minutes: int
    tasks: list[DailyTaskRead] = Field(default_factory=list)
    sessions: list[StudySessionRead] = Field(default_factory=list)
    summary: DaySummary


class CalendarDay(BaseModel):
    date: date
    total_minutes: int = 0
    session_count: int = 0
    completed_tasks: int = 0
    has_activity: bool = False


class CalendarResponse(BaseModel):
    month: str = Field(..., description="YYYY-MM")
    days: list[CalendarDay] = Field(default_factory=list)
    total_minutes: int = 0
    active_days: int = 0
    average_minutes_per_active_day: float = 0.0


class WeekSummary(BaseModel):
    week_start: date
    week_end: date
    total_minutes: int = 0
    total_hours: float = 0.0
    average_minutes_per_day: float = 0.0
    goal_minutes_per_day: int = 0
    days_achieved: int = 0
    tasks_completed: int = 0
    by_category: dict[str, int] = Field(default_factory=dict)
    daily_minutes: dict[str, int] = Field(default_factory=dict)


class StreakRead(BaseModel):
    current_streak: int = 0
    longest_streak: int = 0
    total_active_days: int = 0
    last_active_date: date | None = None
    rule: str = Field(
        default=(
            "A day counts as active when it contains at least one study session or one "
            "completed task with logged minutes."
        )
    )
