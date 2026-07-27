
"""SDK exception hierarchy."""

from __future__ import annotations

from typing import Any


class WorkBuddyError(Exception):
    """Base error for the WorkBuddy Enterprise SDK."""


class WorkBuddyConfigError(WorkBuddyError):
    """Invalid client configuration."""


class WorkBuddyAuthError(WorkBuddyError):
    """Authentication / token acquisition failure."""

    def __init__(
        self,
        message: str,
        *,
        http_status: int | None = None,
        code: int | str | None = None,
        request_id: str | None = None,
        details: Any = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.http_status = http_status
        self.code = code
        self.request_id = request_id
        self.details = details


class WorkBuddyHTTPError(WorkBuddyError):
    """Non-2xx HTTP response."""

    def __init__(
        self,
        message: str,
        *,
        http_status: int,
        code: int | str | None = None,
        request_id: str | None = None,
        body: Any = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.http_status = http_status
        self.code = code
        self.request_id = request_id
        self.body = body


class WorkBuddyAPIError(WorkBuddyError):
    """HTTP 2xx but business code != 0."""

    def __init__(
        self,
        message: str,
        *,
        http_status: int = 200,
        code: int | str | None = None,
        request_id: str | None = None,
        body: Any = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.http_status = http_status
        self.code = code
        self.request_id = request_id
        self.body = body


class WorkBuddyTimeoutError(WorkBuddyError):
    """Request timed out."""

    def __init__(self, message: str = "Request timed out") -> None:
        super().__init__(message)
        self.message = message
