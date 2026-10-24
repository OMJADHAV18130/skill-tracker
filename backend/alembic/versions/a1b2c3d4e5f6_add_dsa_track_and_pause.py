"""Add DSA track and exam pause to preferences

Revision ID: a1b2c3d4e5f6
Revises: 5e86b3d600b4
Create Date: 2026-10-23 10:00:00.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "5e86b3d600b4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "roadmap_phases",
        sa.Column("track", sa.String(length=32), nullable=False, server_default="core"),
    )
    op.create_index(op.f("ix_roadmap_phases_track"), "roadmap_phases", ["track"], unique=False)

    op.add_column("user_preferences", sa.Column("dsa_paused", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("user_preferences", sa.Column("dsa_paused_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("user_preferences", sa.Column("dsa_paused_until", sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column("user_preferences", "dsa_paused_until")
    op.drop_column("user_preferences", "dsa_paused_at")
    op.drop_column("user_preferences", "dsa_paused")
    op.drop_index(op.f("ix_roadmap_phases_track"), table_name="roadmap_phases")
    op.drop_column("roadmap_phases", "track")
