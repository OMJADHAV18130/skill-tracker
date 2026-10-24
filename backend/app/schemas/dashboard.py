"""Dashboard summary schemas."""

from __future__ import annotations

import uuid
from datetime import date

from pydantic import BaseModel, Field


class PhaseProgressDto(BaseModel):
    key: str
    title: str
    month_label: str
    completion_percentage: float
    completed_topics: int
    total_topics: int
    status: str


class DailyStudyPoint(BaseModel):
    date: date
    minutes: int
    goal_minutes: int
    label: str


class MilestoneDto(BaseModel):
    id: str
    title: str
    kind: str = Field(description="topic | project")
    due_label: str | None = None
    completed: bool = False
    subtitle: str | None = None


class ActivityDto(BaseModel):
    id: str
    type: str
    title: str
    detail: str | None = None
    occurred_at: str | None = None


class ProjectStatusDto(BaseModel):
    id: uuid.UUID
    name: str
    status: str
    completion_percentage: float
    completed_milestones: int
    milestone_count: int
    repo_url: str | None = None
    demo_url: str | None = None


class DailyTaskDto(BaseModel):
    id: uuid.UUID
    title: str
    task_date: date
    category: str
    estimated_minutes: int
    priority: str
    is_completed: bool


class DsaTrackDto(BaseModel):
    total_topics: int = 0
    completed_topics: int = 0
    in_progress_topics: int = 0
    completion_percentage: float = 0.0
    paused: bool = False
    paused_until: date | None = None
    phases: list[PhaseProgressDto] = Field(default_factory=list)
    next_recommended_topic: dict[str, str | int | float | None] = Field(default_factory=dict)


class DashboardRead(BaseModel):
    overall_completion_percentage: float = 0.0
    completed_topics: int = 0
    total_topics: int = 0
    in_progress_topics: int = 0
    current_phase: dict[str, str | int | float | None] = Field(default_factory=dict)
    next_recommended_topic: dict[str, str | int | float | None] = Field(default_factory=dict)
    dsa: DsaTrackDto = Field(default_factory=DsaTrackDto)
    total_study_minutes: int = 0
    total_study_hours: float = 0.0
    current_streak: int = 0
    longest_streak: int = 0
    weekly_study: list[DailyStudyPoint] = Field(default_factory=list)
    phase_progress: list[PhaseProgressDto] = Field(default_factory=list)
    todays_tasks: list[DailyTaskDto] = Field(default_factory=list)
    todays_planned_minutes: int = 0
    todays_completed_minutes: int = 0
    todays_goal_minutes: int = 0
    todays_goal_percentage: float = 0.0
    upcoming_milestones: list[MilestoneDto] = Field(default_factory=list)
    recent_activity: list[ActivityDto] = Field(default_factory=list)
    projects: list[ProjectStatusDto] = Field(default_factory=list)
    projects_completed: int = 0
    projects_total: int = 0
