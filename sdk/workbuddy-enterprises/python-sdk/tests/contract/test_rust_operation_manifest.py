"""Keep Rust's handwritten operation manifest aligned with the OpenAPI contract.

The Rust registry is intentionally parsed as source here: Python's contract suite must
not compile or otherwise execute the Rust SDK just to verify metadata.  The parser only
understands the deliberately constrained ``op!`` registry syntax and is insensitive to
whitespace and line wrapping.
"""

from __future__ import annotations

import json
import os
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
import yaml

HTTP_METHODS = {"delete", "get", "head", "options", "patch", "post", "put", "trace"}
ENTERPRISE_PATH_PREFIX = "/enterprises/{enterpriseId}"
EXPECTED_OPERATION_COUNT = 73
READ_ONLY_POSTS = {
    "analytics-activity",
    "analytics-completion",
    "analytics-dialog",
    "analytics-generation",
    "analytics-member-data",
    "licenses-members-query",
    "usage-members-detail",
    "usage-members-limit-query",
    "usage-members-query",
}
MUTATION_EXAMPLES = {
    "users-update",
    "licenses-members-grant",
    "models-custom-create",
    "skills-create",
    "experts-update",
}


@dataclass(frozen=True)
class RustOperation:
    name: str
    method: str
    suffix: str
    path_params: frozenset[str]
    required_query: frozenset[str]
    allowed_query: frozenset[str]
    body_kind: str
    required_body_fields: frozenset[str]
    allowed_body_fields: frozenset[str]
    write: bool

    @property
    def full_path(self) -> str:
        return f"{ENTERPRISE_PATH_PREFIX}{self.suffix}"


def _balanced_block(source: str, opener: int) -> str:
    """Return a balanced Rust delimiter block, preserving its delimiters."""
    pairs = {"(": ")", "[": "]", "{": "}"}
    opening = source[opener]
    assert opening in pairs, f"unsupported delimiter {opening!r}"
    stack = [pairs[opening]]
    quote: str | None = None
    escaped = False
    for index in range(opener + 1, len(source)):
        char = source[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in {'"', "'"}:
            quote = char
        elif char in pairs:
            stack.append(pairs[char])
        elif stack and char == stack[-1]:
            stack.pop()
            if not stack:
                return source[opener : index + 1]
    raise AssertionError(f"unclosed Rust delimiter beginning at offset {opener}")


def _constant_array(source: str, constant: str) -> str:
    marker = f"pub const {constant}"
    start = source.find(marker)
    assert start >= 0, f"Rust constant {constant} not found"
    initializer = source.find("=", start)
    assert initializer >= 0, f"Rust constant {constant} has no initializer"
    opener = source.find("[", initializer)
    assert opener >= 0, f"Rust constant {constant} has no array initializer"
    return _balanced_block(source, opener)


def _split_top_level(source: str) -> list[str]:
    """Split comma-delimited source while respecting strings and delimiters."""
    parts: list[str] = []
    start = 0
    stack: list[str] = []
    pairs = {"(": ")", "[": "]", "{": "}"}
    quote: str | None = None
    escaped = False
    for index, char in enumerate(source):
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in {'"', "'"}:
            quote = char
        elif char in pairs:
            stack.append(pairs[char])
        elif stack and char == stack[-1]:
            stack.pop()
        elif char == "," and not stack:
            token = source[start:index].strip()
            if token:
                parts.append(token)
            start = index + 1
    assert quote is None and not stack, "unbalanced Rust operation metadata"
    token = source[start:].strip()
    if token:
        parts.append(token)
    return parts


def _rust_string(token: str) -> str:
    token = token.strip()
    assert token.startswith('"') and token.endswith('"'), f"expected Rust string literal: {token!r}"
    # The manifest uses ordinary Rust string literals, which share JSON's escaping
    # rules for the syntax used in endpoint metadata.
    return json.loads(token)


def _rust_string_array(token: str) -> frozenset[str]:
    token = token.strip()
    assert token.startswith("[") and token.endswith("]"), f"expected Rust string array: {token!r}"
    return frozenset(_rust_string(item) for item in _split_top_level(token[1:-1]))


def _op_calls(source: str) -> list[str]:
    calls: list[str] = []
    for match in re.finditer(r"\bop!\s*\(", source, flags=re.DOTALL):
        calls.append(_balanced_block(source, source.find("(", match.start())))
    return calls


def _parse_operation_call(call: str) -> RustOperation:
    assert call.startswith("(") and call.endswith(")"), f"malformed op! call: {call!r}"
    fields = _split_top_level(call[1:-1])
    assert len(fields) == 10, f"op! call has {len(fields)} fields, expected 10: {call!r}"
    write_value = fields[9].strip()
    assert write_value in {"true", "false"}, f"op! write must be a bool: {write_value!r}"
    body_kind = fields[6].strip()
    assert body_kind in {"None", "Json", "Multipart"}, f"unsupported body kind: {body_kind!r}"
    return RustOperation(
        name=_rust_string(fields[0]),
        method=_rust_string(fields[1]),
        suffix=_rust_string(fields[2]),
        path_params=_rust_string_array(fields[3]),
        required_query=_rust_string_array(fields[4]),
        allowed_query=_rust_string_array(fields[5]),
        body_kind=body_kind,
        required_body_fields=_rust_string_array(fields[7]),
        allowed_body_fields=_rust_string_array(fields[8]),
        write=write_value == "true",
    )


def _parse_rust_operation_manifest(source: str) -> tuple[list[RustOperation], list[tuple[str, str]]]:
    specs = [_parse_operation_call(call) for call in _op_calls(_constant_array(source, "OPERATION_SPECS"))]
    registry = []
    for entry in _split_top_level(_constant_array(source, "OPENAPI_OPERATIONS")[1:-1]):
        assert entry.startswith("(") and entry.endswith(")"), f"malformed registry tuple: {entry!r}"
        method, path = _split_top_level(entry[1:-1])
        registry.append((_rust_string(method), _rust_string(path)))
    return specs, registry


def _rust_operations_path() -> Path:
    return Path(__file__).resolve().parents[3] / "rust-sdk" / "src" / "operations.rs"


def _load_openapi_spec() -> Mapping[str, Any] | None:
    candidates: list[Path] = []
    configured = os.environ.get("WORKBUDDY_OPENAPI_SPEC")
    if configured:
        candidates.append(Path(configured))
    candidates.append(Path(__file__).resolve().parents[5] / "local" / "codebuddy-openapi-api.yaml")
    for candidate in candidates:
        if candidate.is_file():
            with candidate.open(encoding="utf-8") as stream:
                document = yaml.safe_load(stream)
            if isinstance(document, Mapping):
                return document
    return None


def _resolve_component(
    spec: Mapping[str, Any], value: Mapping[str, Any], section: str,
) -> Mapping[str, Any]:
    while "$ref" in value:
        ref = value["$ref"]
        prefix = f"#/components/{section}/"
        assert isinstance(ref, str) and ref.startswith(prefix), f"unsupported {section} ref: {ref!r}"
        value = spec["components"][section][ref.removeprefix(prefix)]
    return value


def _operation_parameters(
    spec: Mapping[str, Any], path_item: Mapping[str, Any], operation: Mapping[str, Any],
) -> list[Mapping[str, Any]]:
    by_location_and_name: dict[tuple[str, str], Mapping[str, Any]] = {}
    for parameter in [*path_item.get("parameters", []), *operation.get("parameters", [])]:
        resolved = _resolve_component(spec, parameter, "parameters")
        location = resolved.get("in")
        name = resolved.get("name")
        assert isinstance(location, str) and isinstance(name, str), f"invalid parameter: {resolved!r}"
        by_location_and_name[(location, name)] = resolved
    return list(by_location_and_name.values())


def _yaml_body_fields(
    spec: Mapping[str, Any], operation: Mapping[str, Any], expected_kind: str,
) -> tuple[frozenset[str], frozenset[str]]:
    request_body = operation.get("requestBody")
    if expected_kind == "None":
        assert request_body is None, f"unexpected request body: {request_body!r}"
        return frozenset(), frozenset()

    assert isinstance(request_body, Mapping), "expected OpenAPI requestBody"
    request_body = _resolve_component(spec, request_body, "requestBodies")
    expected_media_type = {
        "Json": "application/json",
        "Multipart": "multipart/form-data",
    }[expected_kind]
    content = request_body.get("content")
    assert isinstance(content, Mapping), f"requestBody has no content: {request_body!r}"
    assert set(content) == {expected_media_type}, (
        f"expected only {expected_media_type!r}, got {sorted(content)!r}"
    )
    media = content[expected_media_type]
    assert isinstance(media, Mapping), f"invalid media definition: {media!r}"
    schema = media.get("schema")
    assert isinstance(schema, Mapping), f"requestBody has no schema: {media!r}"
    schema = _resolve_component(spec, schema, "schemas")
    properties = schema.get("properties", {})
    required = schema.get("required", [])
    assert isinstance(properties, Mapping) and isinstance(required, list), f"invalid body schema: {schema!r}"
    return frozenset(properties), frozenset(required)


@pytest.fixture(scope="module")
def rust_manifest() -> tuple[list[RustOperation], list[tuple[str, str]]]:
    return _parse_rust_operation_manifest(_rust_operations_path().read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def openapi_spec() -> Mapping[str, Any] | None:
    return _load_openapi_spec()


def test_rust_operation_manifest_is_self_consistent(rust_manifest) -> None:
    specs, registry = rust_manifest
    assert len(specs) == EXPECTED_OPERATION_COUNT
    assert len(registry) == EXPECTED_OPERATION_COUNT

    names = [spec.name for spec in specs]
    spec_operations = [(spec.method, spec.full_path) for spec in specs]
    assert len(names) == len(set(names)), "Rust operation names must be unique"
    assert len(spec_operations) == len(set(spec_operations)), "Rust method/path pairs must be unique"
    assert len(registry) == len(set(registry)), "OPENAPI_OPERATIONS entries must be unique"
    assert set(registry) == set(spec_operations)

    by_name = {spec.name: spec for spec in specs}
    assert set(by_name) >= READ_ONLY_POSTS, "expected read-only POST examples missing from manifest"
    assert set(by_name) >= MUTATION_EXAMPLES, "expected mutation examples missing from manifest"
    assert {
        spec.name for spec in specs if spec.method == "POST" and not spec.write
    } == READ_ONLY_POSTS
    assert all(by_name[name].method == "POST" and not by_name[name].write for name in READ_ONLY_POSTS)
    assert all(by_name[name].method == "POST" and by_name[name].write for name in MUTATION_EXAMPLES)


def test_rust_operation_manifest_matches_openapi(rust_manifest, openapi_spec) -> None:
    if openapi_spec is None:
        pytest.skip(
            "OpenAPI spec not found; set WORKBUDDY_OPENAPI_SPEC or provide "
            "local/codebuddy-openapi-api.yaml",
        )

    specs, registry = rust_manifest
    paths = openapi_spec.get("paths", {})
    assert isinstance(paths, Mapping), "OpenAPI paths must be a mapping"
    yaml_operations = {
        (method.upper(), path)
        for path, path_item in paths.items()
        if isinstance(path_item, Mapping)
        for method in path_item
        if method.lower() in HTTP_METHODS
    }
    assert set(registry) == yaml_operations

    for rust_operation in specs:
        path_item = paths[rust_operation.full_path]
        assert isinstance(path_item, Mapping), f"missing path {rust_operation.full_path}"
        operation = path_item[rust_operation.method.lower()]
        assert isinstance(operation, Mapping), f"missing method {rust_operation.method}"
        parameters = _operation_parameters(openapi_spec, path_item, operation)

        yaml_path_params = {
            parameter["name"]
            for parameter in parameters
            if parameter["in"] == "path" and parameter["name"] != "enterpriseId"
        }
        yaml_query_params = {
            parameter["name"] for parameter in parameters if parameter["in"] == "query"
        }
        yaml_required_query = {
            parameter["name"]
            for parameter in parameters
            if parameter["in"] == "query" and parameter.get("required")
        }
        assert rust_operation.path_params == yaml_path_params, rust_operation.name
        assert rust_operation.allowed_query == yaml_query_params, rust_operation.name
        assert rust_operation.required_query == yaml_required_query, rust_operation.name

        yaml_fields, yaml_required_fields = _yaml_body_fields(
            openapi_spec, operation, rust_operation.body_kind,
        )
        assert rust_operation.allowed_body_fields == yaml_fields, rust_operation.name
        assert rust_operation.required_body_fields == yaml_required_fields, rust_operation.name
