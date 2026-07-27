
"""Public enums and simple type aliases."""

from __future__ import annotations

from enum import Enum


class SkillSource(str, Enum):
    BUILTIN = "builtin"
    CUSTOM = "custom"


class PublishStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"


class VisibilityType(str, Enum):
    ALL = "all"
    SCOPE_LIST = "scope_list"


class ScopeType(str, Enum):
    USER = "user"
    GROUP = "group"
    DEPARTMENT = "department"


class ModelSource(str, Enum):
    BUILTIN = "builtin"
    CUSTOM = "custom"


class EnableStatus(str, Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"
