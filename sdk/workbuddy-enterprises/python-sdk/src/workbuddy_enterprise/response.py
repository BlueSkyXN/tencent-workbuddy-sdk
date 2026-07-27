
"""Response wrappers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, Mapping, TypeVar

T = TypeVar("T")


@dataclass(slots=True)
class ApiResponse(Generic[T]):
    data: T
    code: int
    message: str
    request_id: str | None
    raw: Mapping[str, Any] | None = None


@dataclass(slots=True)
class Page(Generic[T]):
    items: list[T]
    total_count: int | None = None
    page: int | None = None
    page_num: int | None = None
    page_size: int | None = None
    next_page_token: str | None = None
    extra: Mapping[str, Any] | None = None
