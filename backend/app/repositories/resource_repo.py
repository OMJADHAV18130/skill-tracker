"""Resource library data access."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.resource import UserResourceLink
from app.models.roadmap import Resource


def list_resources(db: Session, user_id: uuid.UUID) -> list[Resource]:
    """Official resources plus the custom ones this user added."""
    return list(
        db.scalars(
            select(Resource)
            .where(
                (Resource.is_official.is_(True))
                | (Resource.created_by_user_id == user_id)
            )
            .order_by(Resource.category, Resource.title)
        ).all()
    )


def get_resource(
    db: Session, resource_id: uuid.UUID, user_id: uuid.UUID | None = None
) -> Resource | None:
    resource = db.get(Resource, resource_id)
    if resource is None:
        return None
    if user_id is not None and not resource.is_official:
        if resource.created_by_user_id != user_id:
            return None
    return resource


def list_links(db: Session, user_id: uuid.UUID) -> list[UserResourceLink]:
    return list(
        db.scalars(
            select(UserResourceLink).where(UserResourceLink.user_id == user_id)
        ).all()
    )


def get_link(db: Session, user_id: uuid.UUID, resource_id: uuid.UUID) -> UserResourceLink | None:
    return db.scalar(
        select(UserResourceLink).where(
            UserResourceLink.user_id == user_id, UserResourceLink.resource_id == resource_id
        )
    )


def create_link(
    db: Session, *, user_id: uuid.UUID, resource_id: uuid.UUID, **values
) -> UserResourceLink:
    link = UserResourceLink(user_id=user_id, resource_id=resource_id, **values)
    db.add(link)
    db.flush()
    return link


def delete_link(db: Session, link: UserResourceLink) -> None:
    db.delete(link)
    db.flush()
