"""Shared response helpers."""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PageMeta(BaseModel):
    page: int = Field(ge=1, description="1-based page number")
    page_size: int = Field(ge=1, description="Items per page")
    total: int = Field(ge=0, description="Total number of matching items")
    pages: int = Field(ge=0, description="Total number of pages")

    @classmethod
    def build(cls, *, page: int, page_size: int, total: int) -> PageMeta:
        pages = (total + page_size - 1) // page_size if page_size else 0
        return cls(page=page, page_size=page_size, total=total, pages=pages)


class Page(BaseModel, Generic[T]):
    items: list[T]
    meta: PageMeta

    @classmethod
    def build(cls, items: list[T], *, page: int, page_size: int, total: int) -> Page[T]:
        return cls(items=items, meta=PageMeta.build(page=page, page_size=page_size, total=total))


class Message(BaseModel):
    message: str


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict[str, Any] | None = None
    request_id: str | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
