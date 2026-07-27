
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping

from workbuddy_enterprise.pagination import parse_page
from workbuddy_enterprise.response import ApiResponse, Page
from workbuddy_enterprise._serialization import as_mapping

if TYPE_CHECKING:
    from workbuddy_enterprise._transport import Transport


class Resource:
    def __init__(self, transport: "Transport") -> None:
        self._t = transport

    def _path(self, suffix: str) -> str:
        return self._t.enterprise_path(suffix)

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
    ) -> ApiResponse[Any]:
        return self._t.request(
            "POST",
            self._path(suffix),
            params=params,
            json_body=body if body is not None else {},
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
        page = parse_page(resp.data)
        return ApiResponse(
            data=page,
            code=resp.code,
            message=resp.message,
            request_id=resp.request_id,
            raw=resp.raw,
        )

    def _as_map(self, resp: ApiResponse[Any]) -> ApiResponse[dict[str, Any]]:
        return ApiResponse(
            data=as_mapping(resp.data),
            code=resp.code,
            message=resp.message,
            request_id=resp.request_id,
            raw=resp.raw,
        )
