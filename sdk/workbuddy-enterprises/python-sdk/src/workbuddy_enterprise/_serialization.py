
"""Wire format helpers."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import fields, is_dataclass
from enum import Enum
from typing import Any


def to_camel(name: str) -> str:
    parts = name.split("_")
    return parts[0] + "".join(p[:1].upper() + p[1:] for p in parts[1:] if p)


def from_camel(name: str) -> str:
    out: list[str] = []
    for ch in name:
        if ch.isupper():
            out.append("_")
            out.append(ch.lower())
        else:
            out.append(ch)
    return "".join(out).lstrip("_")


def dump_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {k: dump_value(v) for k, v in value.items() if v is not None}
    if isinstance(value, (list, tuple)):
        return [dump_value(v) for v in value]
    if hasattr(value, "__dataclass_fields__"):
        return dump_model(value)
    return value


def dump_model(obj: Any, *, by_alias: bool = True) -> dict[str, Any]:
    data: dict[str, Any] = {}
    values: Iterable[tuple[str, Any]]
    if is_dataclass(obj) and not isinstance(obj, type):
        values = ((field.name, getattr(obj, field.name)) for field in fields(obj))
    else:
        values = getattr(obj, "__dict__", {}).items()
    for key, value in values:
        if key.startswith("_"):
            continue
        if value is None:
            continue
        wire_key = to_camel(key) if by_alias else key
        data[wire_key] = dump_value(value)
    return data


def clean_dict(data: Mapping[str, Any] | None) -> dict[str, Any]:
    if not data:
        return {}
    out: dict[str, Any] = {}
    for k, v in data.items():
        if v is None:
            continue
        out[k] = dump_value(v)
    return out


def as_mapping(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, Mapping):
        return dict(value)
    return {"value": value}
