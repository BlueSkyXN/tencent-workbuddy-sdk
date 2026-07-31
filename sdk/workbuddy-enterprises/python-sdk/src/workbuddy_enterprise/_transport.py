
"""HTTP transport for Enterprise OpenAPI."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any, BinaryIO

import httpx

from workbuddy_enterprise._serialization import clean_dict
from workbuddy_enterprise.auth import AuthConfig, TokenProvider
from workbuddy_enterprise.errors import (
    WorkBuddyAPIError,
    WorkBuddyHTTPError,
    WorkBuddyTimeoutError,
)
from workbuddy_enterprise.response import ApiResponse


class Transport:
    def __init__(
        self,
        config: AuthConfig,
        *,
        timeout: float | httpx.Timeout = 30.0,
        transport: httpx.BaseTransport | None = None,
        client: httpx.Client | None = None,
        max_read_retries: int = 2,
    ) -> None:
        self.config = config
        self.max_read_retries = max_read_retries
        self._owns_client = client is None
        self._client = client or httpx.Client(
            base_url=config.base_url.rstrip("/"),
            timeout=timeout,
            transport=transport,
        )
        self._tokens = TokenProvider(config, http_client=self._client, owns_client=False)

    @property
    def enterprise_id(self) -> str:
        return self.config.enterprise_id

    def close(self) -> None:
        self._tokens.close()
        if self._owns_client:
            self._client.close()

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json_body: Mapping[str, Any] | None = None,
        data: Mapping[str, Any] | None = None,
        files: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        expect_json: bool = True,
        retry_read: bool | None = None,
    ) -> ApiResponse[Any]:
        method_u = method.upper()
        if retry_read is None:
            retry_read = method_u in {"GET", "HEAD"}
        attempts = (self.max_read_retries + 1) if retry_read else 1
        last_exc: Exception | None = None
        for attempt in range(attempts):
            try:
                return self._request_once(
                    method_u,
                    path,
                    params=params,
                    json_body=json_body,
                    data=data,
                    files=files,
                    headers=headers,
                    expect_json=expect_json,
                )
            except (WorkBuddyTimeoutError, httpx.TransportError) as exc:
                last_exc = exc
                if attempt + 1 >= attempts:
                    if isinstance(exc, WorkBuddyTimeoutError):
                        raise
                    raise WorkBuddyHTTPError(str(exc), http_status=0) from exc
        assert last_exc is not None
        raise last_exc

    def _request_once(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None,
        json_body: Mapping[str, Any] | None,
        data: Mapping[str, Any] | None,
        files: Mapping[str, Any] | None,
        headers: Mapping[str, str] | None,
        expect_json: bool,
    ) -> ApiResponse[Any]:
        token = self._tokens.get_token()
        req_headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        }
        if headers:
            req_headers.update(headers)

        # Ensure path is absolute against base_url
        url_path = path if path.startswith("/") else f"/{path}"
        try:
            resp = self._client.request(
                method,
                url_path,
                params=clean_dict(params),
                json=clean_dict(json_body) if json_body is not None and files is None and data is None else None,
                data=data,
                files=files,
                headers=req_headers,
            )
        except httpx.TimeoutException as exc:
            raise WorkBuddyTimeoutError("Request timed out") from exc
        except httpx.TransportError:
            raise
        except httpx.HTTPError as exc:
            raise WorkBuddyHTTPError(str(exc), http_status=0) from exc

        request_id = resp.headers.get("X-Request-Id") or resp.headers.get("x-request-id")
        body: Any
        text = resp.text
        if not text:
            body = None
        else:
            try:
                body = resp.json()
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                if expect_json:
                    raise WorkBuddyHTTPError(
                        "Response is not valid JSON",
                        http_status=resp.status_code,
                        request_id=request_id,
                        body=text[:500],
                    ) from exc
                body = text

        if resp.status_code >= 400:
            code = None
            msg = f"HTTP {resp.status_code}"
            if isinstance(body, dict):
                code = body.get("code")
                msg = str(body.get("msg") or body.get("message") or msg)
                request_id = body.get("requestId") or request_id
            raise WorkBuddyHTTPError(
                msg,
                http_status=resp.status_code,
                code=code,
                request_id=request_id,
                body=body,
            )

        if isinstance(body, dict):
            code = body.get("code", 0)
            try:
                code_int = int(code)
            except (TypeError, ValueError):
                code_int = -1 if code not in (None, 0, "0") else 0
            request_id = body.get("requestId") or request_id
            message = str(body.get("msg") or body.get("message") or "OK")
            if code_int != 0:
                raise WorkBuddyAPIError(
                    message,
                    http_status=resp.status_code,
                    code=code_int,
                    request_id=request_id,
                    body=body,
                )
            return ApiResponse(
                data=body.get("data"),
                code=code_int,
                message=message,
                request_id=request_id,
                raw=body,
            )

        return ApiResponse(data=body, code=0, message="OK", request_id=request_id, raw=None)

    def enterprise_path(self, suffix: str) -> str:
        from urllib.parse import quote

        encoded = quote(str(self.enterprise_id), safe="")
        return f"/enterprises/{encoded}{suffix}"


def open_package_file(package: str | Path | BinaryIO | tuple[str, BinaryIO] | None):
    """Return (files dict entry, closer) for multipart package uploads."""
    if package is None:
        return None, None
    if isinstance(package, tuple) and len(package) == 2:
        return {"package": package}, None
    if hasattr(package, "read"):
        name = getattr(package, "name", "package.zip")
        return {"package": (Path(str(name)).name, package)}, None
    path = Path(package)
    fh = path.open("rb")
    return {"package": (path.name, fh)}, fh
