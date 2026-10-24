"""Per-user preferences."""

from __future__ import annotations

import enum
import uuid
from datetime import date, datetime, time
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Time,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, JSONType, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import User

MIN_DAILY_GOAL = 30
MAX_DAILY_GOAL = 480


class Theme(str, enum.Enum):
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


class UserPreference(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "user_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    daily_goal_minutes: Mapped[int] = mapped_column(Integer, default=120, nullable=False)
    roadmap_start_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    theme: Mapped[Theme] = mapped_column(
        Enum(Theme, name="user_theme", native_enum=False, length=10),
        default=Theme.SYSTEM,
        nullable=False,
    )
    reminders_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reminder_time: Mapped[time] = mapped_column(Time, default=time(19, 0), nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), default="UTC", nullable=False)
    # The DSA track can be paused (for example during exams) without losing progress.
    dsa_paused: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    dsa_paused_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    dsa_paused_until: Mapped[date | None] = mapped_column(Date)
    # {phase_key: duration_months} overrides for the roadmap phases
    phase_durations: Mapped[dict] = mapped_column(JSONType, default=dict, nullable=False)
    sidebar_collapsed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped[User] = relationship(back_populates="preference")

    __table_args__ = (UniqueConstraint("user_id", name="uq_user_preferences_user"),)
