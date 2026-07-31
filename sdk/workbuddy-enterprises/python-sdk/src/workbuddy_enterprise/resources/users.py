from __future__ import annotations

from typing import Any

from workbuddy_enterprise._serialization import clean_dict
from workbuddy_enterprise.pagination import page_query, parse_page
from workbuddy_enterprise.resources._base import Resource
from workbuddy_enterprise.response import ApiResponse, Page


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
        plugin_enabled: int | None = None,
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
        if isinstance(resp.data, dict) and (
            "users" in resp.data
            or "items" in resp.data
            or "list" in resp.data
            or "totalCount" in resp.data
        ):
            data: Page[dict[str, Any]] | dict[str, Any] = parse_page(
                resp.data, item_keys=("users", "items", "list", "records"),
            )
        else:
            data = self._as_map(resp).data
        return self._with_data(resp, data)

    def update(self, user_id: str, **fields: Any) -> ApiResponse[dict[str, Any]]:
        mapping = {
            "user_enterprise_name": "userEnterpriseName",
            "userEnterpriseName": "userEnterpriseName",
            # common mistake alias
            "user_name": "userEnterpriseName",
            "userName": "userEnterpriseName",
            "email": "email",
            "phone": "phone",
        }
        body: dict[str, Any] = {}
        for k, v in fields.items():
            if v is None:
                continue
            body[mapping.get(k, k)] = v
        return self._as_map(self._post_json(f"/users/{self._segment(user_id)}/update", body=body))

    def delete(self, user_id: str) -> ApiResponse[dict[str, Any] | None]:
        resp = self._post_json(f"/users/{self._segment(user_id)}/delete", body=None, send_json=False)
        if resp.data is None:
            data: dict[str, Any] | None = None
        else:
            data = self._as_map(resp).data
        return self._with_data(resp, data)

    def update_password(self, user_id: str, *, password: str, **fields: Any) -> ApiResponse[None]:
        body = clean_dict({"password": password, **fields})
        resp = self._post_json(f"/users/{self._segment(user_id)}/password/update", body=body)
        return ApiResponse(None, resp.code, resp.message, resp.request_id, resp.raw)
