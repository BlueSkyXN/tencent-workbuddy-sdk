from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from workbuddy_enterprise._serialization import clean_dict, dump_value
from workbuddy_enterprise.errors import WorkBuddyConfigError
from workbuddy_enterprise.pagination import page_query
from workbuddy_enterprise.resources._base import Resource
from workbuddy_enterprise.response import ApiResponse, Page
from workbuddy_enterprise.types import ModelSource


class ModelsResource(Resource):
    def list_builtin(self) -> ApiResponse[Page[dict[str, Any]] | dict[str, Any]]:
        resp = self._get("/openapi/models/builtin")
        if isinstance(resp.data, dict) and ("items" in resp.data or "list" in resp.data):
            data: Page[dict[str, Any]] | dict[str, Any] = self._as_page(resp).data
        else:
            data = self._as_map(resp).data
        return self._with_data(resp, data)

    def set_builtin_enabled(self, model_id: str, *, enabled: bool) -> ApiResponse[None]:
        resp = self._post_json(
            f"/openapi/models/builtin/{self._segment(model_id)}/toggle",
            body={"enabled": enabled},
        )
        return ApiResponse(None, resp.code, resp.message, resp.request_id, resp.raw)

    def set_builtin_visibility(
        self,
        model_id: str,
        *,
        scope: str,
        user_ids: Sequence[str] | None = None,
        group_ids: Sequence[str] | None = None,
    ) -> ApiResponse[None]:
        return self._set_model_visibility(
            f"/openapi/models/builtin/{self._segment(model_id)}/visibility",
            scope=scope,
            user_ids=user_ids,
            group_ids=group_ids,
        )

    def list_custom(
        self,
        *,
        page_num: int | None = None,
        page_size: int | None = None,
    ) -> ApiResponse[Page[dict[str, Any]]]:
        return self._as_page(
            self._get("/openapi/models/custom", params=page_query(page_num=page_num, page_size=page_size)),
        )

    def create_custom(
        self,
        *,
        display_name: str | None = None,
        provider: str | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
        model_name: str | None = None,
        context_length: int | None = None,
        enabled: bool | None = None,
        scope: str | None = None,
        user_ids: Sequence[str] | None = None,
        group_ids: Sequence[str] | None = None,
        **fields: Any,
    ) -> ApiResponse[dict[str, Any]]:
        mapping = {
            "name": "name",
            "display_name": "displayName",
            "displayName": "displayName",
            "provider": "provider",
            "model_name": "modelName",
            "modelName": "modelName",
            "base_url": "baseUrl",
            "baseUrl": "baseUrl",
            "api_key": "apiKey",
            "apiKey": "apiKey",
            "description": "description",
            "enabled": "enabled",
        }
        body: dict[str, Any] = clean_dict(
            {
                "displayName": display_name,
                "provider": provider,
                "baseUrl": base_url,
                "apiKey": api_key,
                "modelName": model_name,
                "contextLength": context_length,
                "enabled": enabled,
                "scope": scope,
                "userIds": list(user_ids) if user_ids is not None else None,
                "groupIds": list(group_ids) if group_ids is not None else None,
            },
        )
        for k, v in fields.items():
            if v is None:
                continue
            body[mapping.get(k, k)] = dump_value(v)
        required = {"displayName", "provider", "baseUrl", "apiKey", "modelName", "scope"}
        missing = sorted(key for key in required if key not in body)
        if missing:
            raise WorkBuddyConfigError(
                f"models.create_custom requires: {', '.join(missing)}",
            )
        return self._as_map(self._post_json("/openapi/models/custom", body=body))

    def get_custom(self, model_id: str) -> ApiResponse[dict[str, Any]]:
        return self._as_map(self._get(f"/openapi/models/custom/{self._segment(model_id)}"))

    def delete_custom(self, model_id: str) -> ApiResponse[None]:
        resp = self._post_json(f"/openapi/models/custom/{self._segment(model_id)}/delete", body=None, send_json=False)
        return ApiResponse(None, resp.code, resp.message, resp.request_id, resp.raw)

    def set_custom_visibility(
        self,
        model_id: str,
        *,
        scope: str,
        user_ids: Sequence[str] | None = None,
        group_ids: Sequence[str] | None = None,
    ) -> ApiResponse[None]:
        return self._set_model_visibility(
            f"/openapi/models/custom/{self._segment(model_id)}/visibility",
            scope=scope,
            user_ids=user_ids,
            group_ids=group_ids,
        )

    def list_available(self, *, user_id: str) -> ApiResponse[dict[str, Any] | Page[dict[str, Any]]]:
        resp = self._get("/openapi/models/available", params={"userId": user_id})
        if isinstance(resp.data, dict) and "items" in resp.data:
            data: dict[str, Any] | Page[dict[str, Any]] = self._as_page(resp).data
        else:
            data = self._as_map(resp).data
        return self._with_data(resp, data)

    def list(
        self,
        *,
        source: ModelSource | str | None = None,
        page_num: int | None = None,
        page_size: int | None = None,
        enabled: bool | None = None,
        provider: str | None = None,
    ) -> ApiResponse[Page[dict[str, Any]]]:
        params = {
            "source": dump_value(source) if source is not None else None,
            "enabled": enabled,
            "provider": provider,
            **page_query(page_num=page_num, page_size=page_size),
        }
        return self._as_page(self._get("/openapi/models", params=params))

    def get(self, model_id: str) -> ApiResponse[dict[str, Any]]:
        return self._as_map(self._get(f"/openapi/models/{self._segment(model_id)}"))

    def set_enabled(self, model_id: str, *, enabled: bool) -> ApiResponse[None]:
        resp = self._post_json(f"/openapi/models/{self._segment(model_id)}/toggle", body={"enabled": enabled})
        return ApiResponse(None, resp.code, resp.message, resp.request_id, resp.raw)

    def set_visibility(
        self,
        model_id: str,
        *,
        scope: str,
        user_ids: Sequence[str] | None = None,
        group_ids: Sequence[str] | None = None,
    ) -> ApiResponse[None]:
        return self._set_model_visibility(
            f"/openapi/models/{self._segment(model_id)}/visibility",
            scope=scope,
            user_ids=user_ids,
            group_ids=group_ids,
        )

    def _set_model_visibility(
        self,
        suffix: str,
        *,
        scope: str,
        user_ids: Sequence[str] | None,
        group_ids: Sequence[str] | None,
    ) -> ApiResponse[None]:
        body = clean_dict(
            {
                "scope": scope,
                "userIds": list(user_ids) if user_ids is not None else None,
                "groupIds": list(group_ids) if group_ids is not None else None,
            },
        )
        resp = self._post_json(suffix, body=body)
        return ApiResponse(None, resp.code, resp.message, resp.request_id, resp.raw)
