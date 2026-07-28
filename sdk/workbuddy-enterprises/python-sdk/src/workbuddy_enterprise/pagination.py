"""Pagination helpers."""

from __future__ import annotations

from typing import Any, Mapping

from workbuddy_enterprise.response import Page
from workbuddy_enterprise._serialization import as_mapping


def parse_page(data: Any, *, item_keys: tuple[str, ...] | None = None) -> Page[dict[str, Any]]:
    payload = as_mapping(data)
    keys = item_keys or ("items", "list", "records", "users", "members")
    items: list[Any] = []
    for key in keys:
        raw = payload.get(key)
        if isinstance(raw, list):
            items = raw
            break
    page = Page(
        items=[as_mapping(i) for i in items],
        total_count=_as_int(payload.get("totalCount", payload.get("total"))),
        page=_as_int(payload.get("page")),
        page_num=_as_int(payload.get("pageNum")),
        page_size=_as_int(payload.get("pageSize")),
        next_page_token=_as_str(payload.get("nextPageToken")),
        extra=payload,
    )
    # nested pagination object (dashboard member/data)
    nested = payload.get("pagination")
    if isinstance(nested, Mapping):
        if page.total_count is None:
            page.total_count = _as_int(nested.get("totalCount", nested.get("total")))
        if page.page is None:
            page.page = _as_int(nested.get("page"))
        if page.page_num is None:
            page.page_num = _as_int(nested.get("pageNum"))
        if page.page_size is None:
            page.page_size = _as_int(nested.get("pageSize"))
        if page.next_page_token is None:
            page.next_page_token = _as_str(nested.get("nextPageToken"))
    return page


def page_query(
    *,
    page: int | None = None,
    page_num: int | None = None,
    page_size: int | None = None,
    page_token: str | None = None,
) -> dict[str, Any]:
    q: dict[str, Any] = {}
    if page is not None:
        q["page"] = page
    if page_num is not None:
        q["pageNum"] = page_num
    if page_size is not None:
        q["pageSize"] = page_size
    if page_token is not None:
        q["pageToken"] = page_token
    return q


def _as_int(v: Any) -> int | None:
    if v is None or v == "":
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _as_str(v: Any) -> str | None:
    if v is None:
        return None
    return str(v)
