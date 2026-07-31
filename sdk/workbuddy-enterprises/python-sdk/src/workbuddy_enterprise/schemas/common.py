
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from workbuddy_enterprise._serialization import as_mapping
from workbuddy_enterprise.types import ScopeType, VisibilityType


@dataclass(slots=True)
class VisibilityScope:
    scope_type: str
    scope_id: str
    scope_name: str | None = None

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> VisibilityScope:
        m = as_mapping(data)
        return cls(
            scope_type=str(m.get("scopeType") or m.get("scope_type") or ""),
            scope_id=str(m.get("scopeId") or m.get("scope_id") or ""),
            scope_name=(m.get("scopeName") or m.get("scope_name")),
        )

    def to_wire(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "scopeType": self.scope_type if not isinstance(self.scope_type, ScopeType) else self.scope_type.value,
            "scopeId": self.scope_id,
        }
        if self.scope_name is not None:
            out["scopeName"] = self.scope_name
        return out


@dataclass(slots=True)
class VisibilitySpec:
    type: str
    scopes: list[VisibilityScope] = field(default_factory=list)

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> VisibilitySpec:
        m = as_mapping(data)
        scopes_raw = m.get("scopes") or []
        scopes = [VisibilityScope.from_mapping(x) for x in scopes_raw] if isinstance(scopes_raw, list) else []
        return cls(type=str(m.get("type") or ""), scopes=scopes)

    def to_wire(self) -> dict[str, Any]:
        t = self.type.value if isinstance(self.type, VisibilityType) else self.type
        body: dict[str, Any] = {"type": t}
        if self.scopes:
            body["scopes"] = [s.to_wire() for s in self.scopes]
        return body
