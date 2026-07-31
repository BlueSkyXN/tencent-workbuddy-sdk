
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from workbuddy_enterprise._serialization import clean_dict
from workbuddy_enterprise.errors import WorkBuddyConfigError
from workbuddy_enterprise.resources._base import Resource
from workbuddy_enterprise.response import ApiResponse


class LicensesResource(Resource):
    def overview(self) -> ApiResponse[dict[str, Any]]:
        return self._as_map(self._get("/openapi/license/overview"))

    def query_members(
        self,
        *,
        user_ids: Sequence[str] | None = None,
        user_names: Sequence[str] | None = None,
        **fields: Any,
    ) -> ApiResponse[dict[str, Any]]:
        body = clean_dict(
            {
                "userIds": list(user_ids) if user_ids is not None else None,
                "userNames": list(user_names) if user_names is not None else None,
                **fields,
            },
        )
        return self._as_map(self._post_json("/openapi/license/members/query", body=body))

    def grant(
        self,
        *,
        user_ids: Sequence[str] | None = None,
        user_names: Sequence[str] | None = None,
        **fields: Any,
    ) -> ApiResponse[dict[str, Any]]:
        body = clean_dict(
            {
                "userIds": list(user_ids) if user_ids is not None else None,
                "userNames": list(user_names) if user_names is not None else None,
                **fields,
            },
        )
        return self._as_map(self._post_json("/openapi/license/members/grant", body=body))

    def revoke(
        self,
        *,
        user_ids: Sequence[str] | None = None,
        reason: str | None = None,
        **fields: Any,
    ) -> ApiResponse[dict[str, Any]]:
        body = clean_dict(
            {
                "userIds": list(user_ids) if user_ids is not None else None,
                "reason": reason,
                **fields,
            },
        )
        if "userIds" not in body:
            raise WorkBuddyConfigError("licenses.revoke requires user_ids/userIds")
        return self._as_map(self._post_json("/openapi/license/members/revoke", body=body))
