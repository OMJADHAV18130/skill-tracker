"""Daily planner endpoints."""

from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, DbSession, PageDep
from app.schemas.common import Page
from app.schemas.planner import (
    CalendarResponse,
    DailyTaskCreate,
    DailyTaskRead,
    DailyTaskUpdate,
    DayPlanResponse,
    StreakRead,
    StudySessionCreate,
    StudySessionRead,
    TaskCarryForward,
    TaskCompletionUpdate,
    TaskLogTime,
    WeekSummary,
)
from app.services import planner_service

router = APIRouter(prefix="/planner", tags=["planner"])


@router.get(
    "/tasks",
    response_model=Page[DailyTaskRead],
    summary="List daily tasks (paginated, filterable)",
)
def list_tasks(
    db: DbSession,
    current_user: CurrentUser,
    page: PageDep,
    start: date | None = Query(default=None, description="Inclusive start date"),
    end: date | None = Query(default=None, description="Inclusive end date"),
    category: str | None = Query(default=None),
    is_completed: bool | None = Query(default=None),
) -> Page[DailyTaskRead]:
    items, total = planner_service.list_tasks(
        db,
        current_user.id,
        start=start,
        end=end,
        category=category,
        is_completed=is_completed,
        page=page.page,
        page_size=page.page_size,
    )
    return Page.build(
        [DailyTaskRead.model_validate(item) for item in items],
        page=page.page,
        page_size=page.page_size,
        total=total,
    )


@router.post(
    "/tasks",
    response_model=DailyTaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a daily task",
)
def create_task(payload: DailyTaskCreate, db: DbSession, current_user: CurrentUser) -> DailyTaskRead:
    task = planner_service.create_task(db, current_user.id, payload)
    return DailyTaskRead.model_validate(task)


@router.get(
    "/tasks/{task_id}",
    response_model=DailyTaskRead,
    summary="Get a single task",
)
def get_task(task_id: uuid.UUID, db: DbSession, current_user: CurrentUser) -> DailyTaskRead:
    from app.core.errors import NotFoundError
    from app.repositories import planner_repo

    task = planner_repo.get_task(db, current_user.id, task_id)
    if task is None:
        raise NotFoundError("Task not found", code="task_not_found")
    return DailyTaskRead.model_validate(task)


@router.patch(
    "/tasks/{task_id}",
    response_model=DailyTaskRead,
    summary="Update a daily task",
)
def update_task(
    task_id: uuid.UUID,
    payload: DailyTaskUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> DailyTaskRead:
    task = planner_service.update_task(db, current_user.id, task_id, payload)
    return DailyTaskRead.model_validate(task)


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a daily task",
)
def delete_task(task_id: uuid.UUID, db: DbSession, current_user: CurrentUser) -> None:
    planner_service.delete_task(db, current_user.id, task_id)


@router.patch(
    "/tasks/{task_id}/completion",
    response_model=DailyTaskRead,
    summary="Mark a task complete or re-open it",
)
def set_completion(
    task_id: uuid.UUID,
    payload: TaskCompletionUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> DailyTaskRead:
    task = planner_service.set_task_completion(db, current_user.id, task_id, payload)
    return DailyTaskRead.model_validate(task)


@router.post(
    "/tasks/{task_id}/log",
    response_model=DailyTaskRead,
    summary="Log the actual study minutes for a task",
)
def log_time(
    task_id: uuid.UUID,
    payload: TaskLogTime,
    db: DbSession,
    current_user: CurrentUser,
) -> DailyTaskRead:
    task = planner_service.log_task_time(db, current_user.id, task_id, payload)
    return DailyTaskRead.model_validate(task)


@router.post(
    "/tasks/{task_id}/carry-forward",
    response_model=DailyTaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Carry an incomplete task forward to another day",
)
def carry_forward(
    task_id: uuid.UUID,
    payload: TaskCarryForward,
    db: DbSession,
    current_user: CurrentUser,
) -> DailyTaskRead:
    task = planner_service.carry_forward(db, current_user.id, task_id, payload)
    return DailyTaskRead.model_validate(task)


@router.get(
    "/day",
    response_model=DayPlanResponse,
    summary="Planned versus completed work for a single day",
)
def day_plan(
    db: DbSession,
    current_user: CurrentUser,
    target: date = Query(default_factory=date.today, alias="date"),
) -> DayPlanResponse:
    return planner_service.day_plan(db, current_user.id, target)


@router.get(
    "/sessions",
    response_model=list[StudySessionRead],
    summary="Recorded study sessions",
)
def list_sessions(
    db: DbSession,
    current_user: CurrentUser,
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
) -> list[StudySessionRead]:
    sessions = planner_service.list_sessions(db, current_user.id, start=start, end=end)
    return [StudySessionRead.model_validate(s) for s in sessions]


@router.post(
    "/sessions",
    response_model=StudySessionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Record a study session",
)
def create_session(
    payload: StudySessionCreate, db: DbSession, current_user: CurrentUser
) -> StudySessionRead:
    session = planner_service.create_session(db, current_user.id, payload)
    return StudySessionRead.model_validate(session)


@router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a study session",
)
def delete_session(
    session_id: uuid.UUID, db: DbSession, current_user: CurrentUser
) -> None:
    planner_service.delete_session(db, current_user.id, session_id)


@router.get(
    "/calendar",
    response_model=CalendarResponse,
    summary="Monthly calendar of study activity",
)
def calendar_view(
    db: DbSession,
    current_user: CurrentUser,
    year: int = Query(ge=2000, le=2100),
    month: int = Query(ge=1, le=12),
) -> CalendarResponse:
    return planner_service.calendar_view(db, current_user.id, year, month)


@router.get(
    "/week",
    response_model=WeekSummary,
    summary="Summary for a week",
)
def week_summary(
    db: DbSession,
    current_user: CurrentUser,
    anchor: date | None = Query(default=None, description="Any date inside the week"),
) -> WeekSummary:
    return planner_service.week_summary(db, current_user.id, anchor)


@router.get(
    "/streak",
    response_model=StreakRead,
    summary="Current and longest study streak",
)
def streak(db: DbSession, current_user: CurrentUser) -> StreakRead:
    return planner_service.streak(db, current_user.id)
