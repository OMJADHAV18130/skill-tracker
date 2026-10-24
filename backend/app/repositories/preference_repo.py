"""User preference data access."""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.preference import UserPreference


def get_preference(db: Session, user_id: uuid.UUID) -> UserPreference | None:
    return db.scalar(select(UserPreference).where(UserPreference.user_id == user_id))


def get_or_create_preference(db: Session, user_id: uuid.UUID) -> UserPreference:
    pref = get_preference(db, user_id)
    if pref is None:
        pref = UserPreference(user_id=user_id, roadmap_start_date=date.today())
        db.add(pref)
        db.flush()
    return pref
