from __future__ import annotations

from io import BytesIO
from urllib.parse import quote

import httpx
import pytest

from workbuddy_enterprise import WorkBuddyClient
from workbuddy_enterprise.errors import WorkBuddyConfigError

SPECIAL_SEGMENT = "a/b?c#d%中文"
ENCODED_SEGMENT = quote(SPECIAL_SEGMENT, safe="")


@pytest.fixture
def client_and_requests():
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"code": 0, "msg": "OK", "data": {}})

    client = WorkBuddyClient.from_api_key(
        api_key="pt_test",
        enterprise_id="enterprise",
        base_url="https://example.test/api/v1",
        transport=httpx.MockTransport(handler),
    )
    try:
        yield client, requests
    finally:
        client.close()


@pytest.mark.parametrize(
    "invoke",
    [
        lambda client, value: client.users.update(value, email="user@example.com"),
        lambda client, value: client.usage.update_department_quota(
            value, limit_type="limited", new_limit=1,
        ),
        lambda client, value: client.groups.get(value),
        lambda client, value: client.models.get(value),
        lambda client, value: client.skills.get(value),
        lambda client, value: client.skill_categories.delete(value),
        lambda client, value: client.experts.get(value),
        lambda client, value: client.expert_categories.delete(value),
    ],
)
def test_non_enterprise_path_parameters_are_encoded(client_and_requests, invoke):
    client, requests = client_and_requests
    invoke(client, SPECIAL_SEGMENT)
    assert requests[-1].url.raw_path.decode("ascii").count(ENCODED_SEGMENT) == 1


@pytest.mark.parametrize(
    "invoke",
    [
        lambda client: client.skills.update("skill"),
        lambda client: client.experts.update("expert"),
    ],
)
def test_empty_multipart_update_is_rejected_before_request(client_and_requests, invoke):
    client, requests = client_and_requests
    with pytest.raises(WorkBuddyConfigError):
        invoke(client)
    assert requests == []


@pytest.mark.parametrize(
    "invoke",
    [
        lambda client, package: client.skills.create(name="skill", display_name="Skill", package=package),
        lambda client, package: client.skills.update("skill", package=package),
        lambda client, package: client.experts.create(name="expert", display_name="Expert", package=package),
        lambda client, package: client.experts.update("expert", package=package),
    ],
)
def test_multipart_package_field_is_expressible(client_and_requests, invoke):
    client, requests = client_and_requests
    package = BytesIO(b"zip")
    package.name = "package.zip"
    invoke(client, package)
    request = requests[-1]
    assert "multipart/form-data" in request.headers["content-type"]
    assert b'name="package"; filename="package.zip"' in request.content
