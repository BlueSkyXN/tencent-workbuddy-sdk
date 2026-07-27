
from __future__ import annotations

from typing import Any, Sequence

from workbuddy_enterprise.resources._base import Resource
from workbuddy_enterprise.response import ApiResponse
from workbuddy_enterprise._serialization import clean_dict


class LicensesResource(Resource):
    def overview(self) -> ApiResponse[dict[str, Any]]:
        return self._as_map(self._get("/openapi/license/overview"))

    def query_members(self, *, user_ids: Sequence[str] | None = None, **fields: Any) -> ApiResponse[dict[str, Any]]:
        body = clean_dict({"userIds": list(user_ids) if user_ids is not None else None, **fields})
        return self._as_map(self._post_json("/openapi/license/members/query", body=body))

    def grant(self, *, user_ids: Sequence[str] | None = None, **fields: Any) -> ApiResponse[dict[str, Any]]:
        body = clean_dict({"userIds": list(user_ids) if user_ids is not None else None, **fields})
        return self._as_map(self._post_json("/openapi/license/members/grant", body=body))

    def revoke(self, *, user_ids: Sequence[str] | None = None, **fields: Any) -> ApiResponse[dict[str, Any]]:
        body = clean_dict({"userIds": list(user_ids) if user_ids is not None else None, **fields})
        return self._as_map(self._post_json("/openapi/license/members/revoke", body=body))
