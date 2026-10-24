"""Shared roadmap definitions (phases, topics, resources) + per-user progress."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
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


class TopicStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Priority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


TRACK_CORE = "core"
TRACK_DSA = "dsa"
TRACKS = (TRACK_CORE, TRACK_DSA)


class RoadmapPhase(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """One of the learning phases. Shared across all users.

    ``track`` separates the sequential Backend + DevOps curriculum
    (``core``) from the parallel DSA interview track (``dsa``).
    """

    __tablename__ = "roadmap_phases"

    key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    month_label: Mapped[str] = mapped_column(String(64), nullable=False)
    duration_months: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    track: Mapped[str] = mapped_column(
        String(32), default="core", server_default="core", nullable=False, index=True
    )
    project_brief: Mapped[str | None] = mapped_column(Text)
    accent: Mapped[str | None] = mapped_column(String(32))

    topics: Mapped[list[Topic]] = relationship(
        back_populates="phase",
        cascade="all, delete-orphan",
        order_by="Topic.order_index",
        lazy="selectin",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<RoadmapPhase {self.key}>"


class Topic(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A single learnable topic inside a phase. Shared across all users."""

    __tablename__ = "topics"

    phase_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("roadmap_phases.id", ondelete="CASCADE"), nullable=False
    )
    slug: Mapped[str] = mapped_column(String(160), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    subtopics: Mapped[list] = mapped_column(JSONType, default=list, nullable=False)
    is_key_topic: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    phase: Mapped[RoadmapPhase] = relationship(back_populates="topics")
    progress_records: Mapped[list[TopicProgress]] = relationship(
        back_populates="topic", cascade="all, delete-orphan"
    )
    resource_links: Mapped[list[TopicResource]] = relationship(
        back_populates="topic", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_topics_phase_order", "phase_id", "order_index"),
    )


class TopicProgress(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Per-user state of a topic. All roadmap progress is derived from these rows."""

    __tablename__ = "topic_progress"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    topic_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[TopicStatus] = mapped_column(
        Enum(TopicStatus, name="topic_status", native_enum=False, length=20),
        default=TopicStatus.NOT_STARTED,
        nullable=False,
    )
    priority: Mapped[Priority] = mapped_column(
        Enum(Priority, name="topic_priority", native_enum=False, length=10),
        default=Priority.MEDIUM,
        nullable=False,
    )
    rating: Mapped[int | None] = mapped_column(Integer)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    topic: Mapped[Topic] = relationship(back_populates="progress_records")

    __table_args__ = (
        UniqueConstraint("user_id", "topic_id", name="uq_topic_progress_user_topic"),
        Index("ix_topic_progress_user_status", "user_id", "status"),
    )


class TopicNote(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Personal notes attached to a topic."""

    __tablename__ = "topic_notes"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    topic_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)

    topic: Mapped[Topic] = relationship()

    __table_args__ = (Index("ix_topic_notes_user_topic", "user_id", "topic_id"),)


class TopicChecklistItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Personal checklist of subtopics for a topic."""

    __tablename__ = "topic_checklist_items"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    topic_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    is_done: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    topic: Mapped[Topic] = relationship()

    __table_args__ = (Index("ix_topic_checklist_user_topic", "user_id", "topic_id"),)


class Resource(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Curated learning resource (official documentation by default)."""

    __tablename__ = "resources"

    title: Mapped[str] = mapped_column(String(240), nullable=False)
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    tags: Mapped[list] = mapped_column(JSONType, default=list, nullable=False)
    is_official: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # NULL for the shared/official library, set for user-added custom resources.
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    topic_links: Mapped[list[TopicResource]] = relationship(
        back_populates="resource", cascade="all, delete-orphan"
    )


class TopicResource(UUIDPrimaryKeyMixin, Base):
    """Join between topics and resources (seeded recommendations)."""

    __tablename__ = "topic_resources"

    topic_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False
    )
    resource_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("resources.id", ondelete="CASCADE"), nullable=False
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    topic: Mapped[Topic] = relationship(back_populates="resource_links")
    resource: Mapped[Resource] = relationship(back_populates="topic_links")

    __table_args__ = (UniqueConstraint("topic_id", "resource_id", name="uq_topic_resource"),)
