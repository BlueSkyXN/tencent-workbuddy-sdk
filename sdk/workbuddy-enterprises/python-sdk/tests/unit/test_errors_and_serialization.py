
import json
from dataclasses import dataclass

import httpx
import pytest

from workbuddy_enterprise import (
    WorkBuddyAPIError,
    WorkBuddyClient,
    WorkBuddyConfigError,
    WorkBuddyHTTPError,
    WorkBuddyTimeoutError,
)
from workbuddy_enterprise._serialization import dump_model, dump_value, to_camel
from workbuddy_enterprise.schemas.common import VisibilityScope
from workbuddy_enterprise.types import SkillSource


def test_camel_and_enum_dump():
    assert to_camel("page_num") == "pageNum"
    assert dump_value(SkillSource.CUSTOM) == "custom"


def test_http_error(recorder, client_factory):
    def handler(request: httpx.Request) -> httpx.Response:
        recorder.requests.append(request)
        if "oauth2/token" in str(request.url):
            return httpx.Response(200, json={"access_token": "t", "expires_in": 3600})
        return httpx.Response(403, json={"code": 403, "msg": "FORBIDDEN", "requestId": "r1"})

    transport = httpx.MockTransport(handler)
    c = WorkBuddyClient.from_api_key(api_key="pt_x", enterprise_id="ent-1", transport=transport)
    with pytest.raises(WorkBuddyHTTPError) as ei:
        c.skills.list(source="custom")
    assert ei.value.http_status == 403
    assert ei.value.request_id == "r1"
    c.close()


def test_api_error_code_nonzero(client_factory, recorder):
    def handler(request: httpx.Request) -> httpx.Response:
        recorder.requests.append(request)
        if "oauth2/token" in str(request.url):
            return httpx.Response(200, json={"access_token": "t", "expires_in": 3600})
        return httpx.Response(200, json={"code": 1001, "msg": "BIZ", "requestId": "r2", "data": None})

    transport = httpx.MockTransport(handler)
    c = WorkBuddyClient.from_client_credentials(
        client_id="c", client_secret="s", enterprise_id="e", transport=transport,
    )
    with pytest.raises(WorkBuddyAPIError) as ei:
        c.enterprise.get_info()
    assert ei.value.code == 1001
    assert ei.value.request_id == "r2"
    c.close()


def test_invalid_json(client_factory, recorder):
    def handler(request: httpx.Request) -> httpx.Response:
        recorder.requests.append(request)
        if "oauth2/token" in str(request.url):
            return httpx.Response(200, json={"access_token": "t", "expires_in": 3600})
        return httpx.Response(200, content=b"not-json", headers={"content-type": "text/plain"})

    transport = httpx.MockTransport(handler)
    c = WorkBuddyClient.from_client_credentials(
        client_id="c", client_secret="s", enterprise_id="e", transport=transport,
    )
    with pytest.raises(WorkBuddyHTTPError):
        c.enterprise.get_info()
    c.close()


def test_invalid_json_bytes_raise_sdk_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            content=b"\xff",
            headers={
                "content-type": "application/json",
                "x-request-id": "rid-invalid-json",
            },
        )

    c = WorkBuddyClient.from_api_key(
        api_key="pt_x",
        enterprise_id="e",
        transport=httpx.MockTransport(handler),
    )
    try:
        with pytest.raises(WorkBuddyHTTPError) as exc_info:
            c.enterprise.get_info()
        assert exc_info.value.http_status == 200
        assert exc_info.value.request_id == "rid-invalid-json"
    finally:
        c.close()


@pytest.mark.parametrize("error_type", [httpx.ConnectError, httpx.ReadError])
def test_get_transport_errors_are_retried_and_mapped(error_type):
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        raise error_type("transport failed", request=request)

    c = WorkBuddyClient.from_api_key(
        api_key="pt_x",
        enterprise_id="e",
        transport=httpx.MockTransport(handler),
        max_read_retries=2,
    )
    try:
        with pytest.raises(WorkBuddyHTTPError) as exc_info:
            c.enterprise.get_info()
        assert exc_info.value.http_status == 0
        assert len(requests) == 3
    finally:
        c.close()


def test_post_transport_error_is_not_retried():
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        raise httpx.ConnectError("transport failed", request=request)

    c = WorkBuddyClient.from_api_key(
        api_key="pt_x",
        enterprise_id="e",
        transport=httpx.MockTransport(handler),
        max_read_retries=2,
    )
    try:
        with pytest.raises(WorkBuddyHTTPError) as exc_info:
            c.users.update("u1", email="a@example.com")
        assert exc_info.value.http_status == 0
        assert len(requests) == 1
    finally:
        c.close()


def test_get_timeout_is_retried_and_remains_timeout_error():
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        raise httpx.ReadTimeout("timed out", request=request)

    c = WorkBuddyClient.from_api_key(
        api_key="pt_x",
        enterprise_id="e",
        transport=httpx.MockTransport(handler),
        max_read_retries=2,
    )
    try:
        with pytest.raises(WorkBuddyTimeoutError):
            c.enterprise.get_info()
        assert len(requests) == 3
    finally:
        c.close()


def test_slots_dataclass_serialization_preserves_fields():
    scope = VisibilityScope(scope_type="user", scope_id="u1", scope_name="Alice")
    assert dump_value(scope) == {
        "scopeType": "user",
        "scopeId": "u1",
        "scopeName": "Alice",
    }


def test_dump_model_preserves_non_dataclass_dict_fallback():
    @dataclass
    class NestedPayload:
        value: str

    class LegacyPayload:
        def __init__(self) -> None:
            self.display_name = "Legacy"
            self.nested_payload = NestedPayload("nested")
            self._internal = "not-on-wire"

    assert dump_model(LegacyPayload()) == {
        "displayName": "Legacy",
        "nestedPayload": {"value": "nested"},
    }


def test_request_validation_fails_before_transport(client, recorder):
    with pytest.raises(WorkBuddyConfigError):
        client.models.create_custom(display_name="name")
    with pytest.raises(WorkBuddyConfigError):
        client.members.add([{"username": "alice"}])
    with pytest.raises(WorkBuddyConfigError):
        client.licenses.revoke()
    with pytest.raises(WorkBuddyConfigError):
        client.skills.create(name=None, display_name=None)
    with pytest.raises(WorkBuddyConfigError):
        client.experts.create(name=None, display_name=None)
    with pytest.raises(WorkBuddyConfigError):
        client.analytics.activity({})
    for invoke in (client.analytics.dialog, client.analytics.completion, client.analytics.generation):
        with pytest.raises(WorkBuddyConfigError):
            invoke({})
    with pytest.raises(WorkBuddyConfigError):
        client.analytics.member_data(
            {
                "timeRange": {"startTime": "2025-01-01", "endTime": "2025-01-02"},
                "memberFilter": {"type": "all"},
                "clientFilter": {"type": "all"},
                "pluginFilter": {"type": "all"},
                "pagination": {"page": 1},
            },
        )
    assert recorder.requests == []


def test_model_create_custom_accepts_compatible_wire_keys(client, recorder):
    client.models.create_custom(
        displayName="name",
        provider="openai",
        baseUrl="https://api.example.test/v1",
        apiKey="key",
        modelName="model",
        scope="all",
    )
    request = recorder.requests[-1]
    assert request.url.path.endswith("/openapi/models/custom")
    assert json.loads(request.content) == {
        "displayName": "name",
        "provider": "openai",
        "baseUrl": "https://api.example.test/v1",
        "apiKey": "key",
        "modelName": "model",
        "scope": "all",
    }


def test_license_revoke_accepts_compatible_wire_key(client, recorder):
    client.licenses.revoke(userIds=["u1"], reason="offboarding")
    request = recorder.requests[-1]
    assert request.url.path.endswith("/openapi/license/members/revoke")
    assert json.loads(request.content) == {
        "userIds": ["u1"],
        "reason": "offboarding",
    }
