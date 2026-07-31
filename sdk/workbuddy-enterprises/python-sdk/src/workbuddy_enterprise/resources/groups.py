
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from workbuddy_enterprise._serialization import clean_dict
from workbuddy_enterprise.pagination import page_query
from workbuddy_enterprise.resources._base import Resource
from workbuddy_enterprise.response import ApiResponse, Page


class GroupsResource(Resource):
    def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        keyword: str | None = None,
    ) -> ApiResponse[Page[dict[str, Any]]]:
        params = {"keyword": keyword, **page_query(page=page, page_size=page_size)}
        return self._as_page(self._get("/openapi/groups", params=params))

    def get(self, group_id: str) -> ApiResponse[dict[str, Any]]:
        return self._as_map(self._get(f"/openapi/groups/{self._segment(group_id)}"))

    def list_members(
        self,
        group_id: str,
        *,
        page: int | None = None,
        page_size: int | None = None,
        keyword: str | None = None,
    ) -> ApiResponse[Page[dict[str, Any]]]:
        params = {"keyword": keyword, **page_query(page=page, page_size=page_size)}
        return self._as_page(self._get(f"/openapi/groups/{self._segment(group_id)}/members", params=params))

    def add_members(
        self,
        group_id: str,
        *,
        user_ids: Sequence[str] | None = None,
        org_node_ids: Sequence[str] | None = None,
    ) -> ApiResponse[dict[str, Any]]:
        body = clean_dict(
            {
                "userIds": list(user_ids) if user_ids is not None else None,
                "orgNodeIds": list(org_node_ids) if org_node_ids is not None else None,
            },
        )
        return self._as_map(self._post_json(f"/openapi/groups/{self._segment(group_id)}/members/add", body=body))

    def remove_members(
        self,
        group_id: str,
        *,
        user_ids: Sequence[str] | None = None,
        org_node_ids: Sequence[str] | None = None,
    ) -> ApiResponse[dict[str, Any]]:
        body = clean_dict(
            {
                "userIds": list(user_ids) if user_ids is not None else None,
                "orgNodeIds": list(org_node_ids) if org_node_ids is not None else None,
            },
        )
        return self._as_map(self._post_json(f"/openapi/groups/{self._segment(group_id)}/members/remove", body=body))

    def replace_members(
        self,
        group_id: str,
        *,
        user_ids: Sequence[str] | None = None,
        user_names: Sequence[str] | None = None,
        clear_all: bool | None = None,
    ) -> ApiResponse[dict[str, Any]]:
        body = clean_dict(
            {
                "userIds": list(user_ids) if user_ids is not None else None,
                "userNames": list(user_names) if user_names is not None else None,
                "clearAll": clear_all,
            },
        )
        return self._as_map(self._post_json(f"/openapi/groups/{self._segment(group_id)}/members/replace", body=body))
