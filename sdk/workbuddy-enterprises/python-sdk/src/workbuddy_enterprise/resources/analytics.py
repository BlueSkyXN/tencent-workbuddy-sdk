from __future__ import annotations

from typing import Any, Mapping

from workbuddy_enterprise.resources._base import Resource
from workbuddy_enterprise.response import ApiResponse, Page
from workbuddy_enterprise.pagination import parse_page
from workbuddy_enterprise._serialization import clean_dict


class AnalyticsResource(Resource):
    def metrics_download_url_v2(
        self,
        *,
        queries: str,
        range_start: str,
        range_end: str,
        range_step: int,
        **params: Any,
    ) -> ApiResponse[dict[str, Any]]:
        q = clean_dict(
            {
                "queries": queries,
                "range.start": range_start,
                "range.end": range_end,
                "range.step": range_step,
                **params,
            }
        )
        return self._as_map(self._get("/metrics/download_url/v2", params=q))

    def metrics_download_url(
        self,
        *,
        queries: str,
        range_start: str,
        range_end: str,
        range_step: int,
        **params: Any,
    ) -> ApiResponse[dict[str, Any]]:
        q = clean_dict(
            {
                "queries": queries,
                "range.start": range_start,
                "range.end": range_end,
                "range.step": range_step,
                **params,
            }
        )
        return self._as_map(self._get("/metrics/download_url", params=q))

    def metrics(
        self,
        *,
        queries: str,
        range_start: str,
        range_end: str,
        range_step: int,
        **params: Any,
    ) -> ApiResponse[dict[str, Any]]:
        q = clean_dict(
            {
                "queries": queries,
                "range.start": range_start,
                "range.end": range_end,
                "range.step": range_step,
                **params,
            }
        )
        return self._as_map(self._get("/metrics", params=q))

    def activity(self, body: Mapping[str, Any] | None = None, **fields: Any) -> ApiResponse[dict[str, Any]]:
        return self._as_map(self._post_json("/dashboard/analytics/activity", body=clean_dict({**(body or {}), **fields})))

    def dialog(self, body: Mapping[str, Any] | None = None, **fields: Any) -> ApiResponse[dict[str, Any]]:
        return self._as_map(self._post_json("/dashboard/analytics/dialog", body=clean_dict({**(body or {}), **fields})))

    def completion(self, body: Mapping[str, Any] | None = None, **fields: Any) -> ApiResponse[dict[str, Any]]:
        return self._as_map(self._post_json("/dashboard/analytics/completion", body=clean_dict({**(body or {}), **fields})))

    def generation(self, body: Mapping[str, Any] | None = None, **fields: Any) -> ApiResponse[dict[str, Any]]:
        return self._as_map(self._post_json("/dashboard/analytics/generation", body=clean_dict({**(body or {}), **fields})))

    def member_data(self, body: Mapping[str, Any] | None = None, **fields: Any) -> ApiResponse[Page[dict[str, Any]] | dict[str, Any]]:
        resp = self._post_json("/dashboard/member/data", body=clean_dict({**(body or {}), **fields}))
        if isinstance(resp.data, dict) and (
            "items" in resp.data or "list" in resp.data or "members" in resp.data
        ):
            page = parse_page(resp.data, item_keys=("members", "items", "list", "records"))
            return ApiResponse(page, resp.code, resp.message, resp.request_id, resp.raw)
        return self._as_map(resp)
