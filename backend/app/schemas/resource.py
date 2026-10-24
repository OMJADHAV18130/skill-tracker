"""Resource library schemas."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ResourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    url: str
    description: str
    category: str
    tags: list[str] = Field(default_factory=list)
    is_official: bool = True
    is_bookmarked: bool = False
    linked_topic_id: uuid.UUID | None = None
    linked_topic_title: str | None = None
    notes: str | None = None


class ResourceCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=240)
    url: str = Field(..., min_length=8, max_length=1024)
    description: str = Field(default="", max_length=4000)
    category: str = Field(..., min_length=1, max_length=64)
    tags: list[str] = Field(default_factory=list)
    linked_topic_id: uuid.UUID | None = None

    @field_validator("url")
    @classmethod
    def _validate_url(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return cleaned


class ResourceUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=240)
    url: str | None = Field(default=None, min_length=8, max_length=1024)
    description: str | None = Field(default=None, max_length=4000)
    category: str | None = Field(default=None, min_length=1, max_length=64)
    tags: list[str] | None = None
    linked_topic_id: uuid.UUID | None = None

    @field_validator("url")
    @classmethod
    def _validate_url(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned = value.strip()
        if not cleaned.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return cleaned


class ResourceBookmarkUpdate(BaseModel):
    is_bookmarked: bool


class ResourceListResponse(BaseModel):
    items: list[ResourceRead]
    total: int = 0
    categories: list[str] = Field(default_factory=list)
    bookmarked_count: int = 0
