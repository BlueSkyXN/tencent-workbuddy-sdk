
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from workbuddy_enterprise.resources._base import Resource
from workbuddy_enterprise.response import ApiResponse, Page
from workbuddy_enterprise.schemas.skills import SkillSummary  # noqa: F401


class SkillCategoriesResource(Resource):
    def list(self) -> ApiResponse[Page[dict[str, Any]]]:
        resp = self._get("/openapi/skill-categories")
        return self._as_page(resp)

    def create(
        self,
        *,
        name: str,
        description: str | None = None,
        sort_order: int | None = None,
    ) -> ApiResponse[dict[str, Any]]:
        body: dict[str, Any] = {"name": name}
        if description is not None:
            body["description"] = description
        if sort_order is not None:
            body["sortOrder"] = sort_order
        return self._as_map(self._post_json("/openapi/skill-categories", body=body))

    def update(
        self,
        category_id: int,
        *,
        name: str | None = None,
        description: str | None = None,
        sort_order: int | None = None,
    ) -> ApiResponse[None]:
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if sort_order is not None:
            body["sortOrder"] = sort_order
        resp = self._post_json(f"/openapi/skill-categories/{self._segment(category_id)}/update", body=body)
        return ApiResponse(None, resp.code, resp.message, resp.request_id, resp.raw)

    def delete(self, category_id: int) -> ApiResponse[dict[str, Any]]:
        return self._as_map(self._post_json(f"/openapi/skill-categories/{self._segment(category_id)}/delete", body=None, send_json=False))

    def reorder(self, ordered_ids: Sequence[int]) -> ApiResponse[None]:
        resp = self._post_json(
            "/openapi/skill-categories/reorder",
            body={"orderedIds": list(ordered_ids)},
        )
        return ApiResponse(None, resp.code, resp.message, resp.request_id, resp.raw)
