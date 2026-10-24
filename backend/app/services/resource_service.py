"""Resource library service."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.core.errors import ForbiddenError, NotFoundError
from app.repositories import resource_repo
from app.schemas.resource import (
    ResourceBookmarkUpdate,
    ResourceCreate,
    ResourceListResponse,
    ResourceRead,
    ResourceUpdate,
)

CATEGORIES = [
    "Java",
    "Spring Boot",
    "Databases",
    "Security",
    "Linux",
    "Docker",
    "CI/CD",
    "Cloud",
    "Kubernetes",
    "Monitoring",
    "DSA",
    "System Design",
]


def _read(db: Session, resource, link) -> ResourceRead:
    linked_topic_title = None
    if link is not None and link.linked_topic_id is not None:
        from app.repositories import roadmap_repo

        topic = roadmap_repo.get_topic(db, link.linked_topic_id)
        linked_topic_title = topic.title if topic is not None else None
    return ResourceRead(
        id=resource.id,
        title=resource.title,
        url=resource.url,
        description=resource.description,
        category=resource.category,
        tags=list(resource.tags or []),
        is_official=resource.is_official,
        is_bookmarked=bool(link.is_bookmarked) if link is not None else False,
        linked_topic_id=link.linked_topic_id if link is not None else None,
        linked_topic_title=linked_topic_title,
        notes=link.notes if link is not None else None,
    )


def list_resources(
    db: Session,
    user_id: uuid.UUID,
    *,
    query: str | None = None,
    category: str | None = None,
    bookmarked_only: bool = False,
) -> ResourceListResponse:
    resources = resource_repo.list_resources(db, user_id)
    links = {link.resource_id: link for link in resource_repo.list_links(db, user_id)}

    items: list[ResourceRead] = []
    for resource in resources:
        link = links.get(resource.id)
        if category and resource.category.lower() != category.lower():
            continue
        if bookmarked_only and not (link and link.is_bookmarked):
            continue
        if query:
            needle = query.lower()
            haystack = " ".join(
                [
                    resource.title,
                    resource.description,
                    resource.category,
                    " ".join(resource.tags or []),
                ]
            ).lower()
            if needle not in haystack:
                continue
        items.append(_read(db, resource, link))

    categories = sorted({r.category for r in resources})
    return ResourceListResponse(
        items=items,
        total=len(items),
        categories=categories,
        bookmarked_count=sum(1 for link in links.values() if link.is_bookmarked),
    )


def get_resource(db: Session, user_id: uuid.UUID, resource_id: uuid.UUID) -> ResourceRead:
    resource = resource_repo.get_resource(db, resource_id, user_id)
    if resource is None:
        raise NotFoundError("Resource not found", code="resource_not_found")
    link = resource_repo.get_link(db, user_id, resource_id)
    return _read(db, resource, link)


def _get_editable(db: Session, user_id: uuid.UUID, resource_id: uuid.UUID):
    resource = resource_repo.get_resource(db, resource_id, user_id)
    if resource is None:
        raise NotFoundError("Resource not found", code="resource_not_found")
    if resource.created_by_user_id != user_id:
        raise ForbiddenError(
            "Built-in resources cannot be edited or deleted", code="resource_read_only"
        )
    return resource


def create_resource(
    db: Session, user_id: uuid.UUID, payload: ResourceCreate
) -> ResourceRead:
    from app.models.roadmap import Resource

    resource = Resource(
        title=payload.title,
        url=payload.url,
        description=payload.description,
        category=payload.category,
        tags=list(payload.tags),
        is_official=False,
        created_by_user_id=user_id,
    )
    db.add(resource)
    db.flush()
    if payload.linked_topic_id is not None:
        link = resource_repo.create_link(
            db, user_id=user_id, resource_id=resource.id, linked_topic_id=payload.linked_topic_id
        )
        link.is_bookmarked = False
    db.commit()
    db.refresh(resource)
    return get_resource(db, user_id, resource.id)


def update_resource(
    db: Session, user_id: uuid.UUID, resource_id: uuid.UUID, payload: ResourceUpdate
) -> ResourceRead:
    resource = _get_editable(db, user_id, resource_id)
    data = payload.model_dump(exclude_unset=True)
    linked_topic_id = data.pop("linked_topic_id", None)
    for field, value in data.items():
        setattr(resource, field, value)
    if linked_topic_id is not None:
        link = resource_repo.get_link(db, user_id, resource_id)
        if link is None:
            resource_repo.create_link(
                db, user_id=user_id, resource_id=resource_id, linked_topic_id=linked_topic_id
            )
        else:
            link.linked_topic_id = linked_topic_id
    db.commit()
    db.refresh(resource)
    return get_resource(db, user_id, resource_id)


def set_bookmark(
    db: Session, user_id: uuid.UUID, resource_id: uuid.UUID, payload: ResourceBookmarkUpdate
) -> ResourceRead:
    if resource_repo.get_resource(db, resource_id, user_id) is None:
        raise NotFoundError("Resource not found", code="resource_not_found")
    link = resource_repo.get_link(db, user_id, resource_id)
    if link is None:
        link = resource_repo.create_link(
            db, user_id=user_id, resource_id=resource_id, is_bookmarked=payload.is_bookmarked
        )
    else:
        link.is_bookmarked = payload.is_bookmarked
    db.commit()
    return get_resource(db, user_id, resource_id)


def link_to_topic(
    db: Session, user_id: uuid.UUID, resource_id: uuid.UUID, topic_id: uuid.UUID | None
) -> ResourceRead:
    if resource_repo.get_resource(db, resource_id, user_id) is None:
        raise NotFoundError("Resource not found", code="resource_not_found")
    if topic_id is not None:
        from app.repositories import roadmap_repo

        if roadmap_repo.get_topic(db, topic_id) is None:
            raise NotFoundError("Topic not found", code="topic_not_found")
    link = resource_repo.get_link(db, user_id, resource_id)
    if link is None:
        link = resource_repo.create_link(
            db, user_id=user_id, resource_id=resource_id, linked_topic_id=topic_id
        )
    else:
        link.linked_topic_id = topic_id
    db.commit()
    return get_resource(db, user_id, resource_id)


def delete_resource(db: Session, user_id: uuid.UUID, resource_id: uuid.UUID) -> None:
    resource = _get_editable(db, user_id, resource_id)
    link = resource_repo.get_link(db, user_id, resource_id)
    if link is not None:
        resource_repo.delete_link(db, link)
    db.delete(resource)
    db.commit()
