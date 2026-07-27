
from __future__ import annotations

from typing import Any, Sequence

from workbuddy_enterprise.pagination import page_query
from workbuddy_enterprise.resources._base import Resource
from workbuddy_enterprise.response import ApiResponse, Page
from workbuddy_enterprise._serialization import clean_dict


class MembersResource(Resource):
    def list(
        self,
        *,
        page_num: int | None = None,
        page_size: int | None = None,
        keyword: str | None = None,
    ) -> ApiResponse[Page[dict[str, Any]]]:
        params = {"keyword": keyword, **page_query(page_num=page_num, page_size=page_size)}
        return self._as_page(self._get("/openapi/members", params=params))

    def add(self, members: Sequence[dict[str, Any]] | Sequence[str], **body_fields: Any) -> ApiResponse[dict[str, Any]]:
        # Spec: batch add members; accept list of user payloads or emails/ids under common keys.
        if members and isinstance(members[0], str):
            payload: dict[str, Any] = {"userIds": list(members)}
        else:
            payload = {"members": list(members)}
        payload.update(clean_dict(body_fields))
        return self._as_map(self._post_json("/openapi/members/add", body=payload))
