from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from workbuddy_enterprise._serialization import clean_dict
from workbuddy_enterprise.resources._base import Resource
from workbuddy_enterprise.response import ApiResponse, Page


class UsageResource(Resource):
    def get_quota_cycle(self) -> ApiResponse[dict[str, Any]]:
        return self._as_map(self._get("/openapi/usage/quota-cycle"))

    def get_default_quota(self) -> ApiResponse[dict[str, Any]]:
        return self._as_map(self._get("/openapi/usage/default-quota"))

    def update_default_quota(
        self,
        *,
        limit_type: str,
        new_limit: int | None = None,
        cycle_type: str | None = None,
        **fields: Any,
    ) -> ApiResponse[dict[str, Any]]:
        body = clean_dict(
            {
                "limitType": limit_type,
                "newLimit": new_limit,
                "cycleType": cycle_type,
                **fields,
            },
        )
        return self._as_map(self._post_json("/openapi/usage/default-quota/update", body=body))

    def query_members(
        self,
        *,
        user_ids: Sequence[str] | None = None,
        user_names: Sequence[str] | None = None,
        page_num: int | None = None,
        page_size: int | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        **fields: Any,
    ) -> ApiResponse[dict[str, Any]]:
        body = clean_dict(
            {
                "userIds": list(user_ids) if user_ids is not None else None,
                "userNames": list(user_names) if user_names is not None else None,
                "pageNum": page_num,
                "pageSize": page_size,
                "startTime": start_time,
                "endTime": end_time,
                **fields,
            },
        )
        return self._as_map(self._post_json("/openapi/usage/members/query", body=body))

    def query_member_limits(
        self,
        *,
        user_ids: Sequence[str] | None = None,
        user_names: Sequence[str] | None = None,
        page_num: int | None = None,
        page_size: int | None = None,
        **fields: Any,
    ) -> ApiResponse[dict[str, Any]]:
        body = clean_dict(
            {
                "userIds": list(user_ids) if user_ids is not None else None,
                "userNames": list(user_names) if user_names is not None else None,
                "pageNum": page_num,
                "pageSize": page_size,
                **fields,
            },
        )
        return self._as_map(self._post_json("/openapi/usage/members/limit-query", body=body))

    def update_member_quota(
        self,
        *,
        limit_type: str,
        user_ids: Sequence[str] | None = None,
        user_names: Sequence[str] | None = None,
        new_limit: int | None = None,
        cycle_type: str | None = None,
        **fields: Any,
    ) -> ApiResponse[dict[str, Any]]:
        body = clean_dict(
            {
                "limitType": limit_type,
                "userIds": list(user_ids) if user_ids is not None else None,
                "userNames": list(user_names) if user_names is not None else None,
                "newLimit": new_limit,
                "cycleType": cycle_type,
                **fields,
            },
        )
        return self._as_map(self._post_json("/openapi/usage/members/quota/update", body=body))

    def update_department_quota(
        self,
        department_id: str,
        *,
        limit_type: str,
        new_limit: int | None = None,
        cycle_type: str | None = None,
        **fields: Any,
    ) -> ApiResponse[dict[str, Any]]:
        body = clean_dict(
            {
                "limitType": limit_type,
                "newLimit": new_limit,
                "cycleType": cycle_type,
                **fields,
            },
        )
        return self._as_map(
            self._post_json(
                f"/openapi/usage/departments/{self._segment(department_id)}/quota/update",
                body=body,
            ),
        )

    def query_member_details(
        self,
        *,
        time_range: Mapping[str, str],
        department_ids: Sequence[str] | None = None,
        user_ids: Sequence[str] | None = None,
        event_types: Sequence[str] | None = None,
        principal_types: Sequence[str] | None = None,
        page_num: int | None = None,
        page_size: int | None = None,
        group_id: str | None = None,
        version: int | None = None,
        page_token: str | None = None,
        **fields: Any,
    ) -> ApiResponse[Page[dict[str, Any]] | dict[str, Any]]:
        body = clean_dict(
            {
                "timeRange": dict(time_range),
                "departmentIds": list(department_ids) if department_ids is not None else None,
                "userIds": list(user_ids) if user_ids is not None else None,
                "eventTypes": list(event_types) if event_types is not None else None,
                "principalTypes": list(principal_types) if principal_types is not None else None,
                "pageNum": page_num,
                "pageSize": page_size,
                "groupId": group_id,
                "version": version,
                "pageToken": page_token,
                **fields,
            },
        )
        resp = self._post_json("/openapi/usage/members/detail", body=body)
        if isinstance(resp.data, dict) and ("items" in resp.data or "nextPageToken" in resp.data):
            data: Page[dict[str, Any]] | dict[str, Any] = self._as_page(resp).data
        else:
            data = self._as_map(resp).data
        return self._with_data(resp, data)
