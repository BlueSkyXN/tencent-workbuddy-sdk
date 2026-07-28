
from __future__ import annotations

from typing import Any, Sequence

from workbuddy_enterprise.resources._base import Resource
from workbuddy_enterprise.response import ApiResponse, Page


class ExpertCategoriesResource(Resource):
    def list(self) -> ApiResponse[Page[dict[str, Any]]]:
        return self._as_page(self._get("/openapi/expert-categories"))

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
        return self._as_map(self._post_json("/openapi/expert-categories", body=body))

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
        resp = self._post_json(f"/openapi/expert-categories/{category_id}/update", body=body)
        return ApiResponse(None, resp.code, resp.message, resp.request_id, resp.raw)

    def delete(self, category_id: int) -> ApiResponse[dict[str, Any]]:
        return self._as_map(self._post_json(f"/openapi/expert-categories/{category_id}/delete", body=None, send_json=False))

    def reorder(self, ordered_ids: Sequence[int]) -> ApiResponse[None]:
        resp = self._post_json(
            "/openapi/expert-categories/reorder",
            body={"orderedIds": list(ordered_ids)},
        )
        return ApiResponse(None, resp.code, resp.message, resp.request_id, resp.raw)
