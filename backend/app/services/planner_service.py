"""Daily planner service: tasks, study sessions, calendar, streaks."""

from __future__ import annotations

import calendar
import uuid
from datetime import UTC, date, datetime, timedelta

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError, ValidationError
from app.models.planner import DailyTask, StudySession
from app.repositories import planner_repo
from app.schemas.planner import (
    CalendarDay,
    CalendarResponse,
    DailyTaskCreate,
    DailyTaskRead,
    DailyTaskUpdate,
    DayPlanResponse,
    DaySummary,
    StreakRead,
    StudySessionCreate,
    StudySessionRead,
    TaskCompletionUpdate,
    TaskLogTime,
    WeekSummary,
)
from app.services.progress_service import compute_streak


def _day_bounds(target: date) -> tuple[date, date]:
    return target, target


def get_goal_minutes(db: Session, user_id: uuid.UUID) -> int:
    from app.repositories.preference_repo import get_or_create_preference

    pref = get_or_create_preference(db, user_id)
    return pref.daily_goal_minutes


def list_tasks(
    db: Session,
    user_id: uuid.UUID,
    *,
    start: date | None = None,
    end: date | None = None,
    category: str | None = None,
    is_completed: bool | None = None,
    page: int = 1,
    page_size: int = 50,
) -> tuple[list[DailyTask], int]:
    total = planner_repo.count_tasks(
        db, user_id, start=start, end=end, category=category, is_completed=is_completed
    )
    items = planner_repo.list_tasks(
        db,
        user_id,
        start=start,
        end=end,
        category=category,
        is_completed=is_completed,
        limit=page_size,
        offset=(page - 1) * page_size,
    )
    return items, total


def create_task(db: Session, user_id: uuid.UUID, payload: DailyTaskCreate) -> DailyTask:
    task = planner_repo.create_task(
        db,
        user_id=user_id,
        title=payload.title,
        description=payload.description,
        task_date=payload.task_date,
        category=payload.category,
        estimated_minutes=payload.estimated_minutes,
        actual_minutes=payload.actual_minutes,
        priority=payload.priority,
        topic_id=payload.topic_id,
        session_note=payload.session_note,
        is_completed=payload.actual_minutes > 0 and payload.actual_minutes >= payload.estimated_minutes,
        completed_at=(
            datetime.now(UTC) if payload.actual_minutes > 0 else None
        ),
    )
    db.commit()
    db.refresh(task)
    return task


def update_task(
    db: Session, user_id: uuid.UUID, task_id: uuid.UUID, payload: DailyTaskUpdate
) -> DailyTask:
    task = planner_repo.get_task(db, user_id, task_id)
    if task is None:
        raise NotFoundError("Task not found", code="task_not_found")

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        if field == "task_date" and value is None:
            continue
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, user_id: uuid.UUID, task_id: uuid.UUID) -> None:
    task = planner_repo.get_task(db, user_id, task_id)
    if task is None:
        raise NotFoundError("Task not found", code="task_not_found")
    planner_repo.delete_task(db, task)
    db.commit()


def set_task_completion(
    db: Session, user_id: uuid.UUID, task_id: uuid.UUID, payload: TaskCompletionUpdate
) -> DailyTask:
    task = planner_repo.get_task(db, user_id, task_id)
    if task is None:
        raise NotFoundError("Task not found", code="task_not_found")
    task.is_completed = payload.is_completed
    task.completed_at = (
        payload.completed_at or datetime.now(UTC)
        if payload.is_completed
        else None
    )
    db.commit()
    db.refresh(task)
    return task


def log_task_time(
    db: Session, user_id: uuid.UUID, task_id: uuid.UUID, payload: TaskLogTime
) -> DailyTask:
    """Record the minutes actually spent on a task.

    The minutes are stored on the task *and* written as a study session so the
    study-hour totals never double count: the totals are computed from
    ``study_sessions`` only.
    """
    task = planner_repo.get_task(db, user_id, task_id)
    if task is None:
        raise NotFoundError("Task not found", code="task_not_found")

    task.actual_minutes = payload.actual_minutes
    if payload.session_note is not None:
        task.session_note = payload.session_note
    if payload.completed is not None:
        task.is_completed = payload.completed
        task.completed_at = (
            datetime.now(UTC) if payload.completed else None
        )

    # Keep a single study session in sync with the task's logged minutes. Study
    # hour totals are derived from sessions only, so re-logging a task must
    # update the existing session instead of appending a duplicate.
    existing = planner_repo.get_session_for_task(db, user_id, task.id)
    if payload.actual_minutes > 0:
        if existing is None:
            planner_repo.create_session(
                db,
                user_id=user_id,
                task_id=task.id,
                topic_id=task.topic_id,
                session_date=task.task_date,
                minutes=payload.actual_minutes,
                note=payload.session_note,
            )
        else:
            existing.minutes = payload.actual_minutes
            existing.session_date = task.task_date
            existing.topic_id = task.topic_id
            if payload.session_note is not None:
                existing.note = payload.session_note
    elif existing is not None:
        planner_repo.delete_session(db, existing)

    db.commit()
    db.refresh(task)
    return task


def carry_forward(
    db: Session, user_id: uuid.UUID, task_id: uuid.UUID, payload
) -> DailyTask:
    """Move an incomplete task to another day."""
    task = planner_repo.get_task(db, user_id, task_id)
    if task is None:
        raise NotFoundError("Task not found", code="task_not_found")
    if task.is_completed:
        raise ValidationError("Completed tasks cannot be carried forward", code="task_completed")

    target_date = payload.target_date or (task.task_date + timedelta(days=1))
    new_task = planner_repo.create_task(
        db,
        user_id=user_id,
        title=payload.title or task.title,
        description=task.description,
        task_date=target_date,
        category=task.category,
        estimated_minutes=task.estimated_minutes,
        actual_minutes=0,
        priority=task.priority,
        topic_id=task.topic_id,
        carried_from_id=task.id,
        order_index=task.order_index,
    )
    if payload.delete_original:
        planner_repo.delete_task(db, task)
    db.commit()
    db.refresh(new_task)
    return new_task


def create_session(
    db: Session, user_id: uuid.UUID, payload: StudySessionCreate
) -> StudySession:
    if payload.task_id is not None:
        task = planner_repo.get_task(db, user_id, payload.task_id)
        if task is None:
            raise NotFoundError("Task not found", code="task_not_found")
    session = planner_repo.create_session(
        db,
        user_id=user_id,
        minutes=payload.minutes,
        session_date=payload.session_date,
        task_id=payload.task_id,
        topic_id=payload.topic_id,
        note=payload.note,
        created_at=datetime.now(UTC),
    )
    db.commit()
    db.refresh(session)
    return session


def list_sessions(
    db: Session, user_id: uuid.UUID, *, start: date | None = None, end: date | None = None
) -> list[StudySession]:
    return planner_repo.list_sessions(db, user_id, start=start, end=end)


def delete_session(db: Session, user_id: uuid.UUID, session_id: uuid.UUID) -> None:
    session = db.get(StudySession, session_id)
    if session is None or session.user_id != user_id:
        raise NotFoundError("Study session not found", code="session_not_found")
    planner_repo.delete_session(db, session)
    db.commit()


def day_plan(db: Session, user_id: uuid.UUID, target: date) -> DayPlanResponse:
    goal = get_goal_minutes(db, user_id)
    tasks = planner_repo.list_tasks(db, user_id, start=target, end=target, limit=500)
    sessions = planner_repo.list_sessions(db, user_id, start=target, end=target, limit=500)

    planned = sum(t.estimated_minutes for t in tasks)
    completed_tasks = [t for t in tasks if t.is_completed]
    completed_minutes = sum(t.actual_minutes for t in completed_tasks)
    logged = sum(s.minutes for s in sessions)

    summary = DaySummary(
        date=target,
        planned_minutes=planned,
        completed_minutes=completed_minutes,
        logged_minutes=logged,
        planned_tasks=len(tasks),
        completed_tasks=len(completed_tasks),
        goal_minutes=goal,
        goal_percentage=round((logged / goal * 100), 2) if goal else 0.0,
    )
    return DayPlanResponse(
        goal_minutes=goal,
        tasks=[DailyTaskRead.model_validate(t) for t in tasks],
        sessions=[StudySessionRead.model_validate(s) for s in sessions],
        summary=summary,
    )


def calendar_view(db: Session, user_id: uuid.UUID, year: int, month: int) -> CalendarResponse:
    days_in_month = calendar.monthrange(year, month)[1]
    first = date(year, month, 1)
    last = date(year, month, days_in_month)

    minutes_by_day = planner_repo.minutes_by_date(db, user_id, start=first, end=last)
    sessions = planner_repo.list_sessions(db, user_id, start=first, end=last, limit=5000)
    sessions_by_day: dict[date, int] = {}
    for session in sessions:
        sessions_by_day[session.session_date] = sessions_by_day.get(session.session_date, 0) + 1
    tasks = planner_repo.list_tasks(db, user_id, start=first, end=last, limit=2000)

    completed_by_day: dict[date, int] = {}
    for task in tasks:
        if task.is_completed:
            completed_by_day[task.task_date] = completed_by_day.get(task.task_date, 0) + 1

    days: list[CalendarDay] = []
    total = 0
    active = 0
    for day_number in range(1, days_in_month + 1):
        current = date(year, month, day_number)
        minutes = minutes_by_day.get(current, 0)
        total += minutes
        if minutes or completed_by_day.get(current):
            active += 1
        days.append(
            CalendarDay(
                date=current,
                total_minutes=minutes,
                session_count=sessions_by_day.get(current, 0),
                completed_tasks=completed_by_day.get(current, 0),
                has_activity=bool(minutes or completed_by_day.get(current)),
            )
        )

    return CalendarResponse(
        month=f"{year:04d}-{month:02d}",
        days=days,
        total_minutes=total,
        active_days=active,
        average_minutes_per_active_day=round(total / active, 2) if active else 0.0,
    )


def week_summary(db: Session, user_id: uuid.UUID, anchor: date | None = None) -> WeekSummary:
    goal = get_goal_minutes(db, user_id)
    anchor = anchor or date.today()
    week_start = anchor - timedelta(days=anchor.weekday())
    week_end = week_start + timedelta(days=6)

    sessions = planner_repo.list_sessions(db, user_id, start=week_start, end=week_end)
    tasks = planner_repo.list_tasks(db, user_id, start=week_start, end=week_end, limit=1000)

    daily: dict[str, int] = {}
    by_category: dict[str, int] = {}
    for session in sessions:
        key = session.session_date.isoformat()
        daily[key] = daily.get(key, 0) + session.minutes
        task = next((t for t in tasks if t.id == session.task_id), None)
        category = task.category if task else "Uncategorised"
        by_category[category] = by_category.get(category, 0) + session.minutes

    total = sum(s.minutes for s in sessions)
    days_achieved = sum(1 for minutes in daily.values() if minutes >= goal)

    for day_offset in range(7):
        key = (week_start + timedelta(days=day_offset)).isoformat()
        daily.setdefault(key, 0)

    return WeekSummary(
        week_start=week_start,
        week_end=week_end,
        total_minutes=total,
        total_hours=round(total / 60, 2),
        average_minutes_per_day=round(total / 7, 2),
        goal_minutes_per_day=goal,
        days_achieved=days_achieved,
        tasks_completed=sum(1 for t in tasks if t.is_completed),
        by_category=by_category,
        daily_minutes=daily,
    )


def streak(db: Session, user_id: uuid.UUID) -> StreakRead:
    active_dates = planner_repo.active_dates(db, user_id)
    stats = compute_streak(active_dates)
    return StreakRead(
        current_streak=stats.current_streak,
        longest_streak=stats.longest_streak,
        total_active_days=stats.total_active_days,
        last_active_date=stats.last_active_date,
    )


def total_study_minutes(db: Session, user_id: uuid.UUID) -> int:
    return planner_repo.total_minutes(db, user_id)
