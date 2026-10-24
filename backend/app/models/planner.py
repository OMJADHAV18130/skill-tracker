"""Daily planner models: tasks and study sessions."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.roadmap import Priority

if TYPE_CHECKING:
    from app.models.roadmap import Topic


class DailyTask(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A planned unit of work for a specific day."""

    __tablename__ = "daily_tasks"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    task_date: Mapped[date] = mapped_column(Date, nullable=False)
    category: Mapped[str] = mapped_column(String(64), default="General", nullable=False, index=True)
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    actual_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    priority: Mapped[Priority] = mapped_column(
        Enum(Priority, name="task_priority", native_enum=False, length=10),
        default=Priority.MEDIUM,
        nullable=False,
    )
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    session_note: Mapped[str | None] = mapped_column(Text)
    carried_from_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True)
    )
    topic_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("topics.id", ondelete="SET NULL")
    )
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    topic: Mapped[Topic | None] = relationship(lazy="selectin")

    __table_args__ = (
        Index("ix_daily_tasks_user_date", "user_id", "task_date"),
        Index("ix_daily_tasks_user_completed", "user_id", "is_completed"),
    )


class StudySession(UUIDPrimaryKeyMixin, Base):
    """A recorded block of actual study time. The only source of truth for hours."""

    __tablename__ = "study_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    task_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("daily_tasks.id", ondelete="SET NULL")
    )
    topic_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("topics.id", ondelete="SET NULL")
    )
    session_date: Mapped[date] = mapped_column(Date, nullable=False)
    minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    task: Mapped[DailyTask | None] = relationship()
    topic: Mapped[Topic | None] = relationship(lazy="selectin")

    __table_args__ = (
        Index("ix_study_sessions_user_date", "user_id", "session_date"),
        Index("ix_study_sessions_user_task", "user_id", "task_id"),
    )
