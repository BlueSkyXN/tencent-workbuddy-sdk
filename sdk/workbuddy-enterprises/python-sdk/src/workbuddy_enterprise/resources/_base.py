
from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from urllib.parse import quote

from workbuddy_enterprise._serialization import as_mapping
from workbuddy_enterprise.pagination import parse_page
from workbuddy_enterprise.response import ApiResponse, Page

if TYPE_CHECKING:
    from workbuddy_enterprise._transport import Transport

ResponseData = TypeVar("ResponseData")


class Resource:
    def __init__(self, transport: Transport) -> None:
        self._t = transport

    def _path(self, suffix: str) -> str:
        return self._t.enterprise_path(suffix)

    @staticmethod
    def _segment(value: object) -> str:
        """Encode one RFC 3986 path segment without allowing delimiters through."""
        return quote(str(value), safe="")

    def _get(
        self,
        suffix: str,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> ApiResponse[Any]:
        return self._t.request("GET", self._path(suffix), params=params)

    def _post_json(
        self,
        suffix: str,
        *,
        params: Mapping[str, Any] | None = None,
        body: Mapping[str, Any] | None = None,
        send_json: bool = True,
    ) -> ApiResponse[Any]:
        # send_json=False: POST without request body (YAML deletes without requestBody)
        json_body: Mapping[str, Any] | None
        if not send_json:
            json_body = None
        elif body is None:
            json_body = {}
        else:
            json_body = body
        return self._t.request(
            "POST",
            self._path(suffix),
            params=params,
            json_body=json_body,
        )

    def _post_multipart(
        self,
        suffix: str,
        *,
        data: Mapping[str, Any] | None = None,
        files: Mapping[str, Any] | None = None,
    ) -> ApiResponse[Any]:
        return self._t.request(
            "POST",
            self._path(suffix),
            data=data,
            files=files,
        )

    def _as_page(self, resp: ApiResponse[Any]) -> ApiResponse[Page[dict[str, Any]]]:
        return self._with_data(resp, parse_page(resp.data))

    def _as_map(self, resp: ApiResponse[Any]) -> ApiResponse[dict[str, Any]]:
        return self._with_data(resp, as_mapping(resp.data))

    @staticmethod
    def _with_data(
        resp: ApiResponse[Any], data: ResponseData,
    ) -> ApiResponse[ResponseData]:
        return ApiResponse(
            data=data,
            code=resp.code,
            message=resp.message,
            request_id=resp.request_id,
            raw=resp.raw,
        )
