
"""Unofficial WorkBuddy / CodeBuddy Enterprise OpenAPI Python SDK."""

from workbuddy_enterprise.auth import extract_enterprise_ids_from_token
from workbuddy_enterprise.client import WorkBuddyClient
from workbuddy_enterprise.errors import (
    WorkBuddyAPIError,
    WorkBuddyAuthError,
    WorkBuddyConfigError,
    WorkBuddyError,
    WorkBuddyHTTPError,
    WorkBuddyTimeoutError,
)
from workbuddy_enterprise.response import ApiResponse, Page
from workbuddy_enterprise.types import (
    EnableStatus,
    ModelSource,
    PublishStatus,
    ScopeType,
    SkillSource,
    VisibilityType,
)

__all__ = [
    "ApiResponse",
    "EnableStatus",
    "ModelSource",
    "Page",
    "PublishStatus",
    "ScopeType",
    "SkillSource",
    "VisibilityType",
    "WorkBuddyAPIError",
    "WorkBuddyAuthError",
    "WorkBuddyClient",
    "WorkBuddyConfigError",
    "WorkBuddyError",
    "WorkBuddyHTTPError",
    "WorkBuddyTimeoutError",
    "extract_enterprise_ids_from_token",
]

__version__ = "0.1.0"
