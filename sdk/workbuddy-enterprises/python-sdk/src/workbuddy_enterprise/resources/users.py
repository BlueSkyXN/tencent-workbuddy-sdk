
from __future__ import annotations

from typing import Any

from workbuddy_enterprise.pagination import page_query
from workbuddy_enterprise.resources._base import Resource
from workbuddy_enterprise.response import ApiResponse, Page
from workbuddy_enterprise._serialization import clean_dict


class UsersResource(Resource):
    def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        keyword: str | None = None,
        dep: str | None = None,
        include_subtree: bool | None = None,
        is_root: bool | None = None,
        plugin_enabled: bool | None = None,
        use_cache: bool | None = None,
        exact_match: bool | None = None,
    ) -> ApiResponse[Page[dict[str, Any]] | dict[str, Any]]:
        params = {
            "keyword": keyword,
            "dep": dep,
            "include_subtree": include_subtree,
            "is_root": is_root,
            "plugin_enabled": plugin_enabled,
            "use_cache": use_cache,
            "exact_match": exact_match,
            **page_query(page=page, page_size=page_size),
        }
        resp = self._get("/users", params=params)
        if isinstance(resp.data, dict) and ("items" in resp.data or "list" in resp.data or "totalCount" in resp.data):
            return self._as_page(resp)
        return self._as_map(resp)

    def update(self, user_id: str, **fields: Any) -> ApiResponse[dict[str, Any]]:
        mapping = {
            "user_name": "userName",
            "userName": "userName",
            "email": "email",
            "phone": "phone",
            "department_ids": "departmentIds",
            "departmentIds": "departmentIds",
            "status": "status",
        }
        body: dict[str, Any] = {}
        for k, v in fields.items():
            if v is None:
                continue
            body[mapping.get(k, k)] = v
        return self._as_map(self._post_json(f"/users/{user_id}/update", body=body))

    def delete(self, user_id: str) -> ApiResponse[dict[str, Any] | None]:
        resp = self._post_json(f"/users/{user_id}/delete", body={})
        if resp.data is None:
            return ApiResponse(None, resp.code, resp.message, resp.request_id, resp.raw)
        return self._as_map(resp)

    def update_password(self, user_id: str, *, password: str, **fields: Any) -> ApiResponse[None]:
        body = clean_dict({"password": password, **fields})
        resp = self._post_json(f"/users/{user_id}/password/update", body=body)
        return ApiResponse(None, resp.code, resp.message, resp.request_id, resp.raw)
