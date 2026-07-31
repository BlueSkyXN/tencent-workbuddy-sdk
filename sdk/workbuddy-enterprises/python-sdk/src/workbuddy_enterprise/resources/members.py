from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from workbuddy_enterprise._serialization import clean_dict
from workbuddy_enterprise.errors import WorkBuddyConfigError
from workbuddy_enterprise.pagination import page_query
from workbuddy_enterprise.resources._base import Resource
from workbuddy_enterprise.response import ApiResponse, Page


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

    def add(
        self,
        members: Sequence[Mapping[str, Any]],
        *,
        grant_license: bool | None = None,
        **body_fields: Any,
    ) -> ApiResponse[dict[str, Any]]:
        """Batch add members.

        YAML requires body.members[] with at least username + email.
        """
        member_payloads = [dict(member) for member in members]
        for index, member in enumerate(member_payloads):
            missing = [key for key in ("username", "email") if key not in member]
            if missing:
                raise WorkBuddyConfigError(
                    f"members.add members[{index}] requires: {', '.join(missing)}",
                )
        payload: dict[str, Any] = {"members": member_payloads}
        if grant_license is not None:
            payload["grantLicense"] = grant_license
        payload.update(clean_dict(body_fields))
        return self._as_map(self._post_json("/openapi/members/add", body=payload))
