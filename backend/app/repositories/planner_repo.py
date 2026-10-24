"""Planner data access: daily tasks and study sessions."""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.planner import DailyTask, StudySession


def get_task(db: Session, user_id: uuid.UUID, task_id: uuid.UUID) -> DailyTask | None:
    """Ownership is always part of the lookup - never filter after the fetch."""
    return db.scalar(
        select(DailyTask).where(DailyTask.user_id == user_id, DailyTask.id == task_id)
    )


def list_tasks(
    db: Session,
    user_id: uuid.UUID,
    *,
    start: date | None = None,
    end: date | None = None,
    category: str | None = None,
    is_completed: bool | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[DailyTask]:
    stmt = select(DailyTask).where(DailyTask.user_id == user_id)
    if start is not None:
        stmt = stmt.where(DailyTask.task_date >= start)
    if end is not None:
        stmt = stmt.where(DailyTask.task_date <= end)
    if category:
        stmt = stmt.where(DailyTask.category == category)
    if is_completed is not None:
        stmt = stmt.where(DailyTask.is_completed.is_(is_completed))
    stmt = (
        stmt.order_by(DailyTask.task_date, DailyTask.order_index, DailyTask.created_at)
        .limit(limit)
        .offset(offset)
    )
    return list(db.scalars(stmt).all())


def count_tasks(
    db: Session,
    user_id: uuid.UUID,
    *,
    start: date | None = None,
    end: date | None = None,
    category: str | None = None,
    is_completed: bool | None = None,
) -> int:
    stmt = select(func.count()).select_from(DailyTask).where(DailyTask.user_id == user_id)
    if start is not None:
        stmt = stmt.where(DailyTask.task_date >= start)
    if end is not None:
        stmt = stmt.where(DailyTask.task_date <= end)
    if category:
        stmt = stmt.where(DailyTask.category == category)
    if is_completed is not None:
        stmt = stmt.where(DailyTask.is_completed.is_(is_completed))
    return int(db.scalar(stmt) or 0)


def create_task(db: Session, *, user_id: uuid.UUID, **values) -> DailyTask:
    task = DailyTask(user_id=user_id, **values)
    db.add(task)
    db.flush()
    return task


def delete_task(db: Session, task: DailyTask) -> None:
    db.delete(task)
    db.flush()


def list_sessions(
    db: Session,
    user_id: uuid.UUID,
    *,
    start: date | None = None,
    end: date | None = None,
    limit: int = 500,
) -> list[StudySession]:
    stmt = select(StudySession).where(StudySession.user_id == user_id)
    if start is not None:
        stmt = stmt.where(StudySession.session_date >= start)
    if end is not None:
        stmt = stmt.where(StudySession.session_date <= end)
    stmt = stmt.order_by(StudySession.session_date.desc(), StudySession.created_at.desc()).limit(limit)
    return list(db.scalars(stmt).all())


def create_session(db: Session, *, user_id: uuid.UUID, **values) -> StudySession:
    session = StudySession(user_id=user_id, **values)
    db.add(session)
    db.flush()
    return session


def get_session_for_task(
    db: Session, user_id: uuid.UUID, task_id: uuid.UUID
) -> StudySession | None:
    stmt = (
        select(StudySession)
        .where(StudySession.user_id == user_id, StudySession.task_id == task_id)
        .order_by(StudySession.created_at.asc())
        .limit(1)
    )
    return db.scalars(stmt).first()


def delete_session(db: Session, session: StudySession) -> None:
    db.delete(session)
    db.flush()


def total_minutes(
    db: Session, user_id: uuid.UUID, *, start: date | None = None, end: date | None = None
) -> int:
    stmt = select(func.coalesce(func.sum(StudySession.minutes), 0)).where(
        StudySession.user_id == user_id
    )
    if start is not None:
        stmt = stmt.where(StudySession.session_date >= start)
    if end is not None:
        stmt = stmt.where(StudySession.session_date <= end)
    return int(db.scalar(stmt) or 0)


def minutes_by_date(
    db: Session, user_id: uuid.UUID, *, start: date, end: date
) -> dict[date, int]:
    stmt = (
        select(StudySession.session_date, func.sum(StudySession.minutes))
        .where(
            StudySession.user_id == user_id,
            StudySession.session_date >= start,
            StudySession.session_date <= end,
        )
        .group_by(StudySession.session_date)
    )
    return {row[0]: int(row[1] or 0) for row in db.execute(stmt).all()}


def active_dates(db: Session, user_id: uuid.UUID) -> set[date]:
    """Days with at least one study session OR a completed task with logged minutes."""
    session_stmt = select(StudySession.session_date).where(StudySession.user_id == user_id)
    task_stmt = select(DailyTask.task_date).where(
        DailyTask.user_id == user_id,
        DailyTask.is_completed.is_(True),
        DailyTask.actual_minutes > 0,
    )
    dates: set[date] = set()
    dates.update(db.scalars(session_stmt).all())
    dates.update(db.scalars(task_stmt).all())
    return dates
