"""Resource library endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.resource import (
    ResourceBookmarkUpdate,
    ResourceCreate,
    ResourceListResponse,
    ResourceRead,
    ResourceUpdate,
)
from app.services import resource_service

router = APIRouter(prefix="/resources", tags=["resources"])


@router.get(
    "",
    response_model=ResourceListResponse,
    summary="Search and filter the resource library",
)
def list_resources(
    db: DbSession,
    current_user: CurrentUser,
    q: str | None = Query(default=None, description="Free text search"),
    category: str | None = Query(default=None, description="Filter by category"),
    bookmarked: bool | None = Query(default=None, description="Only bookmarked resources"),
) -> ResourceListResponse:
    return resource_service.list_resources(
        db,
        current_user.id,
        query=q,
        category=category,
        bookmarked_only=bool(bookmarked),
    )


@router.get(
    "/categories",
    response_model=list[str],
    summary="Available resource categories",
)
def categories() -> list[str]:
    return sorted(set(resource_service.CATEGORIES))


@router.post(
    "",
    response_model=ResourceRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add a custom resource",
)
def create_resource(
    payload: ResourceCreate, db: DbSession, current_user: CurrentUser
) -> ResourceRead:
    return resource_service.create_resource(db, current_user.id, payload)


@router.get("/{resource_id}", response_model=ResourceRead, summary="Get a resource")
def get_resource(
    resource_id: uuid.UUID, db: DbSession, current_user: CurrentUser
) -> ResourceRead:
    return resource_service.get_resource(db, current_user.id, resource_id)


@router.patch(
    "/{resource_id}", response_model=ResourceRead, summary="Update a custom resource"
)
def update_resource(
    resource_id: uuid.UUID,
    payload: ResourceUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> ResourceRead:
    return resource_service.update_resource(db, current_user.id, resource_id, payload)


@router.put(
    "/{resource_id}/bookmark",
    response_model=ResourceRead,
    summary="Bookmark or un-bookmark a resource",
)
def set_bookmark(
    resource_id: uuid.UUID,
    payload: ResourceBookmarkUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> ResourceRead:
    return resource_service.set_bookmark(db, current_user.id, resource_id, payload)


@router.put(
    "/{resource_id}/link",
    response_model=ResourceRead,
    summary="Link a resource to a roadmap topic",
)
def link_topic(
    resource_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
    topic_id: uuid.UUID | None = Query(default=None),
) -> ResourceRead:
    return resource_service.link_to_topic(db, current_user.id, resource_id, topic_id)


@router.delete(
    "/{resource_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a custom resource",
)
def delete_resource(
    resource_id: uuid.UUID, db: DbSession, current_user: CurrentUser
) -> None:
    resource_service.delete_resource(db, current_user.id, resource_id)
