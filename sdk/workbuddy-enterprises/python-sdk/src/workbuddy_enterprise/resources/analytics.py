from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from workbuddy_enterprise._serialization import clean_dict
from workbuddy_enterprise.errors import WorkBuddyConfigError
from workbuddy_enterprise.pagination import parse_page
from workbuddy_enterprise.resources._base import Resource
from workbuddy_enterprise.response import ApiResponse, Page


class AnalyticsResource(Resource):
    @staticmethod
    def _validated_body(
        body: Mapping[str, Any] | None,
        fields: Mapping[str, Any],
        *,
        required: tuple[str, ...],
        require_view_type: bool = False,
        require_activity_options: bool = False,
        require_pagination: bool = False,
    ) -> dict[str, Any]:
        payload = clean_dict({**(body or {}), **fields})
        missing = [key for key in required if key not in payload]
        time_range = payload.get("timeRange")
        if not isinstance(time_range, Mapping) or not all(
            key in time_range for key in ("startTime", "endTime")
        ):
            missing.append("timeRange.startTime/endTime")
        for filter_name in ("memberFilter", "clientFilter", "pluginFilter"):
            filter_value = payload.get(filter_name)
            if not isinstance(filter_value, Mapping) or filter_value.get("type") not in {"all", "selected"}:
                missing.append(f"{filter_name}.type")
        if require_view_type and payload.get("viewType") not in {"metrics", "trends"}:
            missing.append("viewType(metrics|trends)")
        if require_activity_options:
            options = payload.get("activityOptions")
            if not isinstance(options, Mapping) or "distributionDimension" not in options:
                missing.append("activityOptions.distributionDimension")
        if require_pagination:
            pagination = payload.get("pagination")
            if not isinstance(pagination, Mapping) or not all(
                key in pagination for key in ("page", "pageSize")
            ):
                missing.append("pagination.page/pageSize")
        if missing:
            raise WorkBuddyConfigError(
                f"analytics request requires: {', '.join(dict.fromkeys(missing))}",
            )
        return payload

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
            },
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
            },
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
            },
        )
        return self._as_map(self._get("/metrics", params=q))

    def activity(self, body: Mapping[str, Any] | None = None, **fields: Any) -> ApiResponse[dict[str, Any]]:
        payload = self._validated_body(
            body,
            fields,
            required=("timeRange", "memberFilter", "clientFilter", "pluginFilter", "viewType", "activityOptions"),
            require_view_type=True,
            require_activity_options=True,
        )
        return self._as_map(self._post_json("/dashboard/analytics/activity", body=payload))

    def dialog(self, body: Mapping[str, Any] | None = None, **fields: Any) -> ApiResponse[dict[str, Any]]:
        payload = self._validated_body(
            body, fields, required=("timeRange", "memberFilter", "clientFilter", "pluginFilter", "viewType"), require_view_type=True,
        )
        return self._as_map(self._post_json("/dashboard/analytics/dialog", body=payload))

    def completion(self, body: Mapping[str, Any] | None = None, **fields: Any) -> ApiResponse[dict[str, Any]]:
        payload = self._validated_body(
            body, fields, required=("timeRange", "memberFilter", "clientFilter", "pluginFilter", "viewType"), require_view_type=True,
        )
        return self._as_map(self._post_json("/dashboard/analytics/completion", body=payload))

    def generation(self, body: Mapping[str, Any] | None = None, **fields: Any) -> ApiResponse[dict[str, Any]]:
        payload = self._validated_body(
            body, fields, required=("timeRange", "memberFilter", "clientFilter", "pluginFilter", "viewType"), require_view_type=True,
        )
        return self._as_map(self._post_json("/dashboard/analytics/generation", body=payload))

    def member_data(self, body: Mapping[str, Any] | None = None, **fields: Any) -> ApiResponse[Page[dict[str, Any]] | dict[str, Any]]:
        payload = self._validated_body(
            body, fields, required=("timeRange", "memberFilter", "clientFilter", "pluginFilter", "pagination"), require_pagination=True,
        )
        resp = self._post_json("/dashboard/member/data", body=payload)
        if isinstance(resp.data, dict) and (
            "items" in resp.data or "list" in resp.data or "members" in resp.data
        ):
            data: Page[dict[str, Any]] | dict[str, Any] = parse_page(
                resp.data, item_keys=("members", "items", "list", "records"),
            )
        else:
            data = self._as_map(resp).data
        return self._with_data(resp, data)
