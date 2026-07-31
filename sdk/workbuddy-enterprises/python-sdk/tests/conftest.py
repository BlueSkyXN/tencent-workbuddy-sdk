
from __future__ import annotations

from collections.abc import Callable
from typing import Any

import httpx
import pytest

from workbuddy_enterprise import WorkBuddyClient


class Recorder:
    def __init__(self) -> None:
        self.requests: list[httpx.Request] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        # token endpoint
        if request.url.path.endswith("/oauth2/token") or str(request.url).endswith("/oauth2/token"):
            return httpx.Response(
                200,
                json={"access_token": "test-token", "expires_in": 3600, "token_type": "Bearer"},
            )
        # default success envelope
        return httpx.Response(
            200,
            json={
                "code": 0,
                "msg": "OK",
                "requestId": "req-test-1",
                "data": {"items": [], "totalCount": 0, "pageNum": 1, "pageSize": 20},
            },
        )


@pytest.fixture
def recorder() -> Recorder:
    return Recorder()


@pytest.fixture
def client_factory(recorder: Recorder) -> Callable[..., WorkBuddyClient]:
    def _make(**kwargs: Any) -> WorkBuddyClient:
        transport = httpx.MockTransport(recorder.handler)
        return WorkBuddyClient.from_client_credentials(
            client_id="cid",
            client_secret="csecret",
            enterprise_id="ent-1",
            token_url="https://copilot.tencent.com/oauth2/token",
            base_url="https://api.copilot.tencent.com/api/v1",
            transport=transport,
            **kwargs,
        )
    return _make


@pytest.fixture
def client(client_factory: Callable[..., WorkBuddyClient]):
    c = client_factory()
    yield c
    c.close()
