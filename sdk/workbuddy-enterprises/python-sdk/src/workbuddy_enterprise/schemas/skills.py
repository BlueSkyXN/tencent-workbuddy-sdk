
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from workbuddy_enterprise._serialization import as_mapping


@dataclass(slots=True)
class SkillSummary:
    skill_id: str | None = None
    source: str | None = None
    item_ref: str | None = None
    name: str | None = None
    display_name: str | None = None
    icon: str | None = None
    version: str | None = None
    category_id: str | None = None
    category_name: str | None = None
    publish_status: str | None = None
    enabled: bool | None = None
    disabled_reason: str | None = None
    updated_at: str | None = None
    updated_by: str | None = None
    raw: Mapping[str, Any] | None = None

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "SkillSummary":
        m = as_mapping(data)
        return cls(
            skill_id=m.get("skillId"),
            source=m.get("source"),
            item_ref=m.get("itemRef"),
            name=m.get("name"),
            display_name=m.get("displayName"),
            icon=m.get("icon"),
            version=m.get("version"),
            category_id=str(m["categoryId"]) if m.get("categoryId") is not None else None,
            category_name=m.get("categoryName"),
            publish_status=m.get("publishStatus"),
            enabled=m.get("enabled"),
            disabled_reason=m.get("disabledReason"),
            updated_at=m.get("updatedAt"),
            updated_by=m.get("updatedBy"),
            raw=m,
        )


@dataclass(slots=True)
class SkillDetail:
    skill_id: str | None = None
    name: str | None = None
    display_name: str | None = None
    display_name_en: str | None = None
    description_zh: str | None = None
    description_en: str | None = None
    icon: str | None = None
    custom_category_id: int | None = None
    version: str | None = None
    publish_status: str | None = None
    status: str | None = None
    disabled_reason: str | None = None
    zip_file_name: str | None = None
    zip_md5: str | None = None
    zip_sha256: str | None = None
    zip_size_bytes: int | None = None
    creator_name: str | None = None
    updated_by: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    raw: Mapping[str, Any] | None = None

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "SkillDetail":
        m = as_mapping(data)
        return cls(
            skill_id=m.get("skillId"),
            name=m.get("name"),
            display_name=m.get("displayName"),
            display_name_en=m.get("displayNameEn"),
            description_zh=m.get("descriptionZh"),
            description_en=m.get("descriptionEn"),
            icon=m.get("icon"),
            custom_category_id=m.get("customCategoryId"),
            version=m.get("version"),
            publish_status=m.get("publishStatus"),
            status=m.get("status"),
            disabled_reason=m.get("disabledReason"),
            zip_file_name=m.get("zipFileName"),
            zip_md5=m.get("zipMd5"),
            zip_sha256=m.get("zipSha256"),
            zip_size_bytes=m.get("zipSizeBytes"),
            creator_name=m.get("creatorName"),
            updated_by=m.get("updatedBy"),
            created_at=m.get("createdAt"),
            updated_at=m.get("updatedAt"),
            raw=m,
        )
