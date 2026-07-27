
import httpx
import pytest

from workbuddy_enterprise import WorkBuddyAPIError, WorkBuddyClient, WorkBuddyHTTPError
from workbuddy_enterprise._serialization import to_camel, dump_value
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
        client_id="c", client_secret="s", enterprise_id="e", transport=transport
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
        client_id="c", client_secret="s", enterprise_id="e", transport=transport
    )
    with pytest.raises(WorkBuddyHTTPError):
        c.enterprise.get_info()
    c.close()
