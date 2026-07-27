
"""Unofficial WorkBuddy / CodeBuddy Enterprise OpenAPI Python SDK."""

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
from workbuddy_enterprise.auth import extract_enterprise_ids_from_token

__all__ = [
    "WorkBuddyClient",
    "ApiResponse",
    "Page",
    "WorkBuddyError",
    "WorkBuddyConfigError",
    "WorkBuddyAuthError",
    "WorkBuddyHTTPError",
    "WorkBuddyAPIError",
    "WorkBuddyTimeoutError",
    "SkillSource",
    "PublishStatus",
    "VisibilityType",
    "ScopeType",
    "ModelSource",
    "EnableStatus",
    "extract_enterprise_ids_from_token",
]

__version__ = "0.1.0"
