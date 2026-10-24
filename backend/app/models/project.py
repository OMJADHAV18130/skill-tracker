"""Project tracker models."""

from __future__ import annotations

import enum
import uuid
from datetime import date, datetime

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
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, JSONType, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.roadmap import Priority


class ProjectStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Project(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A portfolio project tracked by the user."""

    __tablename__ = "projects"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    required_skills: Mapped[list] = mapped_column(JSONType, default=list, nullable=False)
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus, name="project_status", native_enum=False, length=20),
        default=ProjectStatus.NOT_STARTED,
        nullable=False,
    )
    priority: Mapped[Priority] = mapped_column(
        Enum(Priority, name="project_priority", native_enum=False, length=10),
        default=Priority.MEDIUM,
        nullable=False,
    )
    start_date: Mapped[date | None] = mapped_column(Date)
    target_date: Mapped[date | None] = mapped_column(Date)
    repo_url: Mapped[str | None] = mapped_column(String(512))
    demo_url: Mapped[str | None] = mapped_column(String(512))
    notes: Mapped[str | None] = mapped_column(Text)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    milestones: Mapped[list[ProjectMilestone]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="ProjectMilestone.order_index",
        lazy="selectin",
    )
    checklist_items: Mapped[list[ProjectChecklistItem]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="ProjectChecklistItem.order_index",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_projects_user_order", "user_id", "order_index"),
        UniqueConstraint("user_id", "name", name="uq_projects_user_name"),
    )


class ProjectMilestone(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "project_milestones"

    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    due_date: Mapped[date | None] = mapped_column(Date)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    project: Mapped[Project] = relationship(back_populates="milestones")

    __table_args__ = (Index("ix_project_milestones_project_order", "project_id", "order_index"),)


class ProjectChecklistItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "project_checklist_items"

    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    is_done: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    project: Mapped[Project] = relationship(back_populates="checklist_items")

    __table_args__ = (
        Index("ix_project_checklist_project_order", "project_id", "order_index"),
    )
