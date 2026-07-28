
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

import httpx
import pytest

from workbuddy_enterprise import WorkBuddyClient
from workbuddy_enterprise.types import SkillSource


def ok(data: Any = None) -> httpx.Response:
    return httpx.Response(
        200,
        json={"code": 0, "msg": "OK", "requestId": "rid", "data": data if data is not None else {}},
    )


def make_client(handler) -> WorkBuddyClient:
    return WorkBuddyClient.from_client_credentials(
        client_id="cid",
        client_secret="csecret",
        enterprise_id="ent-1",
        token_url="https://copilot.tencent.com/oauth2/token",
        base_url="https://api.copilot.tencent.com/api/v1",
        transport=httpx.MockTransport(handler),
    )


def last_api_request(reqs: list[httpx.Request]) -> httpx.Request:
    api_reqs = [r for r in reqs if "/oauth2/token" not in str(r.url)]
    assert api_reqs, "no API request recorded"
    return api_reqs[-1]


def assert_req(
    req: httpx.Request,
    *,
    method: str,
    path_suffix: str,
    query: dict[str, str] | None = None,
    json_body: dict[str, Any] | None = None,
    multipart: bool = False,
):
    assert req.method == method
    assert path_suffix in req.url.path
    assert req.url.path.endswith(path_suffix) or path_suffix in req.url.path
    if query:
        for k, v in query.items():
            assert req.url.params.get(k) == str(v)
    if json_body is not None:
        ctype = req.headers.get("content-type", "")
        assert "application/json" in ctype
        assert json.loads(req.content.decode()) == json_body
    if multipart:
        ctype = req.headers.get("content-type", "")
        assert "multipart/form-data" in ctype


# Each entry: id, method, path_suffix, invoker, optional asserts
# invoker(client) -> None

def _cases() -> list[tuple]:
    cases = []

    def add(op_id, method, suffix, invoker, **expect):
        cases.append((op_id, method, suffix, invoker, expect))

    # enterprise 2
    add("enterprise.get_info", "GET", "/enterprises/ent-1/info", lambda c: c.enterprise.get_info())
    add("enterprise.get_license", "GET", "/enterprises/ent-1/license", lambda c: c.enterprise.get_license())

    # users 4
    add("users.list", "GET", "/enterprises/ent-1/users", lambda c: c.users.list(page=1, page_size=20), query={"page": "1", "pageSize": "20"})
    add("users.update", "POST", "/enterprises/ent-1/users/u1/update", lambda c: c.users.update("u1", user_enterprise_name="a"), json_body={"userEnterpriseName": "a"})
    add("users.delete", "POST", "/enterprises/ent-1/users/u1/delete", lambda c: c.users.delete("u1"), no_body=True)
    add("users.update_password", "POST", "/enterprises/ent-1/users/u1/password/update", lambda c: c.users.update_password("u1", password="p"), json_body={"password": "p"})

    # members 2
    add("members.list", "GET", "/enterprises/ent-1/openapi/members", lambda c: c.members.list(page_num=1, page_size=20, keyword="k"), query={"pageNum": "1", "pageSize": "20", "keyword": "k"})
    add("members.add", "POST", "/enterprises/ent-1/openapi/members/add", lambda c: c.members.add([{"username": "alice", "email": "a@example.com"}]), json_body={"members": [{"username": "alice", "email": "a@example.com"}]})

    # licenses 4
    add("licenses.overview", "GET", "/enterprises/ent-1/openapi/license/overview", lambda c: c.licenses.overview())
    add("licenses.query_members", "POST", "/enterprises/ent-1/openapi/license/members/query", lambda c: c.licenses.query_members(user_ids=["u1"]), json_body={"userIds": ["u1"]})
    add("licenses.grant", "POST", "/enterprises/ent-1/openapi/license/members/grant", lambda c: c.licenses.grant(user_ids=["u1"]), json_body={"userIds": ["u1"]})
    add("licenses.revoke", "POST", "/enterprises/ent-1/openapi/license/members/revoke", lambda c: c.licenses.revoke(user_ids=["u1"]), json_body={"userIds": ["u1"]})

    # usage 8
    add("usage.get_quota_cycle", "GET", "/enterprises/ent-1/openapi/usage/quota-cycle", lambda c: c.usage.get_quota_cycle())
    add("usage.get_default_quota", "GET", "/enterprises/ent-1/openapi/usage/default-quota", lambda c: c.usage.get_default_quota())
    add("usage.update_default_quota", "POST", "/enterprises/ent-1/openapi/usage/default-quota/update", lambda c: c.usage.update_default_quota(limit_type="limited", new_limit=100), json_body={"limitType": "limited", "newLimit": 100})
    add("usage.query_members", "POST", "/enterprises/ent-1/openapi/usage/members/query", lambda c: c.usage.query_members(user_ids=["u1"]), json_body={"userIds": ["u1"]})
    add("usage.query_member_limits", "POST", "/enterprises/ent-1/openapi/usage/members/limit-query", lambda c: c.usage.query_member_limits(user_ids=["u1"]), json_body={"userIds": ["u1"]})
    add("usage.update_member_quota", "POST", "/enterprises/ent-1/openapi/usage/members/quota/update", lambda c: c.usage.update_member_quota(limit_type="limited", user_ids=["u1"], new_limit=5000), json_body={"limitType": "limited", "userIds": ["u1"], "newLimit": 5000})
    add("usage.update_department_quota", "POST", "/enterprises/ent-1/openapi/usage/departments/d1/quota/update", lambda c: c.usage.update_department_quota("d1", limit_type="limited", new_limit=9), json_body={"limitType": "limited", "newLimit": 9})
    add(
        "usage.query_member_details",
        "POST",
        "/enterprises/ent-1/openapi/usage/members/detail",
        lambda c: c.usage.query_member_details(
            time_range={"startTime": "2025-01-01T00:00:00+08:00", "endTime": "2025-01-02T00:00:00+08:00"},
            version=2,
            page_token="",
            page_size=100,
        ),
        json_body={
            "timeRange": {"startTime": "2025-01-01T00:00:00+08:00", "endTime": "2025-01-02T00:00:00+08:00"},
            "pageSize": 100,
            "version": 2,
            "pageToken": "",
        },
    )

    # groups 6
    add("groups.list", "GET", "/enterprises/ent-1/openapi/groups", lambda c: c.groups.list(page=1, page_size=20), query={"page": "1", "pageSize": "20"})
    add("groups.get", "GET", "/enterprises/ent-1/openapi/groups/g1", lambda c: c.groups.get("g1"))
    add("groups.list_members", "GET", "/enterprises/ent-1/openapi/groups/g1/members", lambda c: c.groups.list_members("g1", page=1, page_size=10), query={"page": "1", "pageSize": "10"})
    add("groups.add_members", "POST", "/enterprises/ent-1/openapi/groups/g1/members/add", lambda c: c.groups.add_members("g1", user_ids=["u1"], org_node_ids=["o1"]), json_body={"userIds": ["u1"], "orgNodeIds": ["o1"]})
    add("groups.remove_members", "POST", "/enterprises/ent-1/openapi/groups/g1/members/remove", lambda c: c.groups.remove_members("g1", user_ids=["u1"]), json_body={"userIds": ["u1"]})
    add("groups.replace_members", "POST", "/enterprises/ent-1/openapi/groups/g1/members/replace", lambda c: c.groups.replace_members("g1", user_ids=["u1"], clear_all=False), json_body={"userIds": ["u1"], "clearAll": False})

    # models 13
    add("models.list_builtin", "GET", "/enterprises/ent-1/openapi/models/builtin", lambda c: c.models.list_builtin())
    add("models.set_builtin_enabled", "POST", "/enterprises/ent-1/openapi/models/builtin/m1/toggle", lambda c: c.models.set_builtin_enabled("m1", enabled=False), json_body={"enabled": False})
    add("models.set_builtin_visibility", "POST", "/enterprises/ent-1/openapi/models/builtin/m1/visibility", lambda c: c.models.set_builtin_visibility("m1", scope="all"), json_body={"scope": "all"})
    add("models.list_custom", "GET", "/enterprises/ent-1/openapi/models/custom", lambda c: c.models.list_custom(page_num=1, page_size=20), query={"pageNum": "1", "pageSize": "20"})
    add("models.create_custom", "POST", "/enterprises/ent-1/openapi/models/custom", lambda c: c.models.create_custom(name="n", display_name="N"), json_body={"name": "n", "displayName": "N"})
    add("models.get_custom", "GET", "/enterprises/ent-1/openapi/models/custom/m2", lambda c: c.models.get_custom("m2"))
    add("models.delete_custom", "POST", "/enterprises/ent-1/openapi/models/custom/m2/delete", lambda c: c.models.delete_custom("m2"), no_body=True)
    add("models.set_custom_visibility", "POST", "/enterprises/ent-1/openapi/models/custom/m2/visibility", lambda c: c.models.set_custom_visibility("m2", scope="all"), json_body={"scope": "all"})
    add("models.list_available", "GET", "/enterprises/ent-1/openapi/models/available", lambda c: c.models.list_available(user_id="u1"), query={"userId": "u1"})
    add("models.list", "GET", "/enterprises/ent-1/openapi/models", lambda c: c.models.list(source="custom", page_num=1, page_size=10), query={"source": "custom", "pageNum": "1", "pageSize": "10"})
    add("models.get", "GET", "/enterprises/ent-1/openapi/models/m3", lambda c: c.models.get("m3"))
    add("models.set_enabled", "POST", "/enterprises/ent-1/openapi/models/m3/toggle", lambda c: c.models.set_enabled("m3", enabled=True), json_body={"enabled": True})
    add("models.set_visibility", "POST", "/enterprises/ent-1/openapi/models/m3/visibility", lambda c: c.models.set_visibility("m3", scope="all"), json_body={"scope": "all"})

    # skills 8
    add("skills.list", "GET", "/enterprises/ent-1/openapi/skills", lambda c: c.skills.list(source=SkillSource.CUSTOM, page_num=1, page_size=20), query={"source": "custom", "pageNum": "1", "pageSize": "20"})
    add("skills.create", "POST", "/enterprises/ent-1/openapi/skills", lambda c: c.skills.create(name="n", display_name="N", publish_status="draft"), multipart=True)
    add("skills.get", "GET", "/enterprises/ent-1/openapi/skills/sk-1", lambda c: c.skills.get("sk-1"))
    add("skills.update", "POST", "/enterprises/ent-1/openapi/skills/sk-1/update", lambda c: c.skills.update("sk-1", version="1.1.0"), multipart=True)
    add("skills.delete", "POST", "/enterprises/ent-1/openapi/skills/sk-1/delete", lambda c: c.skills.delete("sk-1"), no_body=True)
    add("skills.set_enabled", "POST", "/enterprises/ent-1/openapi/skills/sk-1/toggle", lambda c: c.skills.set_enabled("sk-1", source="custom", enabled=False, disabled_reason="x"), query={"source": "custom"}, json_body={"enabled": False, "disabledReason": "x"})
    add("skills.set_visibility", "POST", "/enterprises/ent-1/openapi/skills/sk-1/visibility", lambda c: c.skills.set_visibility("sk-1", source="custom", type="all"), query={"source": "custom"}, json_body={"type": "all"})
    add("skills.get_visibility", "GET", "/enterprises/ent-1/openapi/skills/sk-1/visibility", lambda c: c.skills.get_visibility("sk-1", source="custom"), query={"source": "custom"})

    # skill categories 5
    add("skill_categories.list", "GET", "/enterprises/ent-1/openapi/skill-categories", lambda c: c.skill_categories.list())
    add("skill_categories.create", "POST", "/enterprises/ent-1/openapi/skill-categories", lambda c: c.skill_categories.create(name="研发", sort_order=1), json_body={"name": "研发", "sortOrder": 1})
    add("skill_categories.update", "POST", "/enterprises/ent-1/openapi/skill-categories/10/update", lambda c: c.skill_categories.update(10, name="x"), json_body={"name": "x"})
    add("skill_categories.delete", "POST", "/enterprises/ent-1/openapi/skill-categories/10/delete", lambda c: c.skill_categories.delete(10), no_body=True)
    add("skill_categories.reorder", "POST", "/enterprises/ent-1/openapi/skill-categories/reorder", lambda c: c.skill_categories.reorder([3, 1, 2]), json_body={"orderedIds": [3, 1, 2]})

    # experts 8
    add("experts.list", "GET", "/enterprises/ent-1/openapi/experts", lambda c: c.experts.list(source="custom"), query={"source": "custom"})
    add("experts.create", "POST", "/enterprises/ent-1/openapi/experts", lambda c: c.experts.create(name="n", display_name="N"), multipart=True)
    add("experts.get", "GET", "/enterprises/ent-1/openapi/experts/ex-1", lambda c: c.experts.get("ex-1"))
    add("experts.update", "POST", "/enterprises/ent-1/openapi/experts/ex-1/update", lambda c: c.experts.update("ex-1", version="1.0.1"), multipart=True)
    add("experts.delete", "POST", "/enterprises/ent-1/openapi/experts/ex-1/delete", lambda c: c.experts.delete("ex-1"), no_body=True)
    add("experts.set_enabled", "POST", "/enterprises/ent-1/openapi/experts/ex-1/toggle", lambda c: c.experts.set_enabled("ex-1", source="custom", enabled=True), query={"source": "custom"}, json_body={"enabled": True})
    add("experts.set_visibility", "POST", "/enterprises/ent-1/openapi/experts/ex-1/visibility", lambda c: c.experts.set_visibility("ex-1", source="custom", type="all"), query={"source": "custom"}, json_body={"type": "all"})
    add("experts.get_visibility", "GET", "/enterprises/ent-1/openapi/experts/ex-1/visibility", lambda c: c.experts.get_visibility("ex-1", source="custom"), query={"source": "custom"})

    # expert categories 5
    add("expert_categories.list", "GET", "/enterprises/ent-1/openapi/expert-categories", lambda c: c.expert_categories.list())
    add("expert_categories.create", "POST", "/enterprises/ent-1/openapi/expert-categories", lambda c: c.expert_categories.create(name="e"), json_body={"name": "e"})
    add("expert_categories.update", "POST", "/enterprises/ent-1/openapi/expert-categories/2/update", lambda c: c.expert_categories.update(2, description="d"), json_body={"description": "d"})
    add("expert_categories.delete", "POST", "/enterprises/ent-1/openapi/expert-categories/2/delete", lambda c: c.expert_categories.delete(2), no_body=True)
    add("expert_categories.reorder", "POST", "/enterprises/ent-1/openapi/expert-categories/reorder", lambda c: c.expert_categories.reorder([1, 2]), json_body={"orderedIds": [1, 2]})

    # analytics 8
    add("analytics.metrics_download_url_v2", "GET", "/enterprises/ent-1/metrics/download_url/v2", lambda c: c.analytics.metrics_download_url_v2(queries="q1", range_start="2025-03-20 00:00:00", range_end="2025-03-20 00:00:00", range_step=86400), query={"queries": "q1", "range.start": "2025-03-20 00:00:00", "range.end": "2025-03-20 00:00:00", "range.step": "86400"})
    add("analytics.metrics_download_url", "GET", "/enterprises/ent-1/metrics/download_url", lambda c: c.analytics.metrics_download_url(queries="q1", range_start="2025-03-20 00:00:00", range_end="2025-03-20 00:00:00", range_step=86400), query={"queries": "q1", "range.start": "2025-03-20 00:00:00", "range.end": "2025-03-20 00:00:00", "range.step": "86400"})
    add("analytics.metrics", "GET", "/enterprises/ent-1/metrics", lambda c: c.analytics.metrics(queries="q1", range_start="2025-03-20 00:00:00", range_end="2025-03-20 00:00:00", range_step=86400), query={"queries": "q1", "range.start": "2025-03-20 00:00:00", "range.end": "2025-03-20 00:00:00", "range.step": "86400"})
    add("analytics.activity", "POST", "/enterprises/ent-1/dashboard/analytics/activity", lambda c: c.analytics.activity({"foo": 1}), json_body={"foo": 1})
    add("analytics.dialog", "POST", "/enterprises/ent-1/dashboard/analytics/dialog", lambda c: c.analytics.dialog({"foo": 1}), json_body={"foo": 1})
    add("analytics.completion", "POST", "/enterprises/ent-1/dashboard/analytics/completion", lambda c: c.analytics.completion({"foo": 1}), json_body={"foo": 1})
    add("analytics.generation", "POST", "/enterprises/ent-1/dashboard/analytics/generation", lambda c: c.analytics.generation({"foo": 1}), json_body={"foo": 1})
    add("analytics.member_data", "POST", "/enterprises/ent-1/dashboard/member/data", lambda c: c.analytics.member_data({"page": 1}), json_body={"page": 1})

    return cases


CASES = _cases()


@pytest.mark.parametrize("op_id,method,suffix,invoker,expect", CASES, ids=[c[0] for c in CASES])
def test_operation_contract(op_id, method, suffix, invoker, expect):
    reqs: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        reqs.append(request)
        if "oauth2/token" in str(request.url):
            return httpx.Response(200, json={"access_token": "t", "expires_in": 3600})
        data: Any = {"items": [], "totalCount": 0}
        if "visibility" in request.url.path and request.method == "GET":
            data = {"skillId": "sk-1", "type": "all", "scopes": []}
        return ok(data)

    client = make_client(handler)
    try:
        invoker(client)
    finally:
        client.close()

    req = last_api_request(reqs)
    assert_req(
        req,
        method=method,
        path_suffix=suffix,
        query=expect.get("query"),
        json_body=expect.get("json_body"),
        multipart=bool(expect.get("multipart")),
    )
    # auth header present and not logging secrets elsewhere
    assert req.headers.get("Authorization") == "Bearer t"


def test_operation_count_is_73():
    assert len(CASES) == 73
