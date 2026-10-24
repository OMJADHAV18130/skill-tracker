"""Per-user resource state (bookmarks, custom links to topics)."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.roadmap import Resource


class UserResourceLink(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A user's personal link between a resource and (optionally) a topic."""

    __tablename__ = "user_resource_links"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    resource_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("resources.id", ondelete="CASCADE"), nullable=False
    )
    linked_topic_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("topics.id", ondelete="SET NULL")
    )
    is_bookmarked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    custom_url: Mapped[str | None] = mapped_column(String(1024))
    notes: Mapped[str | None] = mapped_column(String(1000))
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    resource: Mapped[Resource] = relationship(lazy="selectin")

    __table_args__ = (
        UniqueConstraint("user_id", "resource_id", name="uq_user_resource_link"),
        Index("ix_user_resource_links_user_bookmark", "user_id", "is_bookmarked"),
    )
