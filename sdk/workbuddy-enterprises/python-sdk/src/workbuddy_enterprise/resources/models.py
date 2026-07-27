
from __future__ import annotations

from typing import Any, Mapping

from workbuddy_enterprise.pagination import page_query
from workbuddy_enterprise.resources._base import Resource
from workbuddy_enterprise.response import ApiResponse, Page
from workbuddy_enterprise.schemas.common import VisibilityScope, VisibilitySpec
from workbuddy_enterprise.types import ModelSource, VisibilityType
from workbuddy_enterprise._serialization import clean_dict, dump_value


class ModelsResource(Resource):
    def list_builtin(self) -> ApiResponse[Page[dict[str, Any]] | dict[str, Any]]:
        resp = self._get("/openapi/models/builtin")
        # some list endpoints return items page, others list directly
        if isinstance(resp.data, dict) and ("items" in resp.data or "list" in resp.data):
            return self._as_page(resp)
        return self._as_map(resp)

    def set_builtin_enabled(self, model_id: str, *, enabled: bool) -> ApiResponse[None]:
        resp = self._post_json(
            f"/openapi/models/builtin/{model_id}/toggle",
            body={"enabled": enabled},
        )
        return ApiResponse(None, resp.code, resp.message, resp.request_id, resp.raw)

    def set_builtin_visibility(
        self,
        model_id: str,
        *,
        type: VisibilityType | str,
        scopes: list[VisibilityScope | Mapping[str, Any]] | None = None,
    ) -> ApiResponse[None]:
        return self._set_visibility(f"/openapi/models/builtin/{model_id}/visibility", type=type, scopes=scopes)

    def list_custom(
        self,
        *,
        page_num: int | None = None,
        page_size: int | None = None,
    ) -> ApiResponse[Page[dict[str, Any]]]:
        return self._as_page(
            self._get("/openapi/models/custom", params=page_query(page_num=page_num, page_size=page_size))
        )

    def create_custom(self, **fields: Any) -> ApiResponse[dict[str, Any]]:
        # Accept snake_case keys and map common ones; also allow already-camel keys via **fields
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
        body: dict[str, Any] = {}
        for k, v in fields.items():
            if v is None:
                continue
            body[mapping.get(k, k)] = dump_value(v)
        return self._as_map(self._post_json("/openapi/models/custom", body=body))

    def get_custom(self, model_id: str) -> ApiResponse[dict[str, Any]]:
        return self._as_map(self._get(f"/openapi/models/custom/{model_id}"))

    def delete_custom(self, model_id: str) -> ApiResponse[None]:
        resp = self._post_json(f"/openapi/models/custom/{model_id}/delete", body={})
        return ApiResponse(None, resp.code, resp.message, resp.request_id, resp.raw)

    def set_custom_visibility(
        self,
        model_id: str,
        *,
        type: VisibilityType | str,
        scopes: list[VisibilityScope | Mapping[str, Any]] | None = None,
    ) -> ApiResponse[None]:
        return self._set_visibility(f"/openapi/models/custom/{model_id}/visibility", type=type, scopes=scopes)

    def list_available(self, *, user_id: str) -> ApiResponse[dict[str, Any] | Page[dict[str, Any]]]:
        resp = self._get("/openapi/models/available", params={"userId": user_id})
        if isinstance(resp.data, dict) and "items" in resp.data:
            return self._as_page(resp)
        return self._as_map(resp)

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
        return self._as_map(self._get(f"/openapi/models/{model_id}"))

    def set_enabled(self, model_id: str, *, enabled: bool) -> ApiResponse[None]:
        resp = self._post_json(f"/openapi/models/{model_id}/toggle", body={"enabled": enabled})
        return ApiResponse(None, resp.code, resp.message, resp.request_id, resp.raw)

    def set_visibility(
        self,
        model_id: str,
        *,
        type: VisibilityType | str,
        scopes: list[VisibilityScope | Mapping[str, Any]] | None = None,
    ) -> ApiResponse[None]:
        return self._set_visibility(f"/openapi/models/{model_id}/visibility", type=type, scopes=scopes)

    def _set_visibility(
        self,
        suffix: str,
        *,
        type: VisibilityType | str,
        scopes: list[VisibilityScope | Mapping[str, Any]] | None,
    ) -> ApiResponse[None]:
        scope_objs: list[VisibilityScope] = []
        for s in scopes or []:
            if isinstance(s, VisibilityScope):
                scope_objs.append(s)
            else:
                scope_objs.append(VisibilityScope.from_mapping(s))
        body = VisibilitySpec(type=dump_value(type), scopes=scope_objs).to_wire()
        resp = self._post_json(suffix, body=body)
        return ApiResponse(None, resp.code, resp.message, resp.request_id, resp.raw)
