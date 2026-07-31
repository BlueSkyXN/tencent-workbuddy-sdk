
from __future__ import annotations

import json
import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import httpx
import pytest
import yaml

from workbuddy_enterprise import WorkBuddyClient
from workbuddy_enterprise.types import SkillSource

HTTP_METHODS = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}
_ADDITIONAL_PROPERTIES_UNSET = object()


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
    no_body: bool = False,
):
    assert req.method == method
    assert req.url.path.endswith(path_suffix)
    if query:
        for k, v in query.items():
            assert req.url.params.get(k) == str(v)
    if no_body:
        assert req.content == b""
        assert "content-type" not in req.headers
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

    dashboard_filters = {
        "timeRange": {
            "startTime": "2025-01-01T00:00:00+08:00",
            "endTime": "2025-01-02T00:00:00+08:00",
        },
        "memberFilter": {"type": "all", "data": []},
        "clientFilter": {"type": "all", "data": []},
        "pluginFilter": {"type": "all", "data": []},
    }

    # enterprise 2
    add("enterprise.get_info", "GET", "/enterprises/ent-1/info", lambda c: c.enterprise.get_info())
    add("enterprise.get_license", "GET", "/enterprises/ent-1/license", lambda c: c.enterprise.get_license())

    # users 4
    add("users.list", "GET", "/enterprises/ent-1/users", lambda c: c.users.list(page=1, page_size=20, keyword="k", dep="d", include_subtree=True, is_root=False, plugin_enabled=1, use_cache=True, exact_match=False), query={"page": "1", "pageSize": "20", "keyword": "k", "dep": "d", "include_subtree": "true", "is_root": "false", "plugin_enabled": "1", "use_cache": "true", "exact_match": "false"})
    add("users.update", "POST", "/enterprises/ent-1/users/u1/update", lambda c: c.users.update("u1", user_enterprise_name="a", phone="+8613800000000", email="a@example.com"), json_body={"userEnterpriseName": "a", "phone": "+8613800000000", "email": "a@example.com"})
    add("users.delete", "POST", "/enterprises/ent-1/users/u1/delete", lambda c: c.users.delete("u1"), no_body=True)
    add("users.update_password", "POST", "/enterprises/ent-1/users/u1/password/update", lambda c: c.users.update_password("u1", password="p"), json_body={"password": "p"})

    # members 2
    add("members.list", "GET", "/enterprises/ent-1/openapi/members", lambda c: c.members.list(page_num=1, page_size=20, keyword="k"), query={"pageNum": "1", "pageSize": "20", "keyword": "k"})
    add("members.add", "POST", "/enterprises/ent-1/openapi/members/add", lambda c: c.members.add([{"username": "alice", "email": "a@example.com", "firstName": "Alice", "lastName": "Wang", "initialPassword": "Tencent@2026"}], grant_license=True), json_body={"members": [{"username": "alice", "email": "a@example.com", "firstName": "Alice", "lastName": "Wang", "initialPassword": "Tencent@2026"}], "grantLicense": True})

    # licenses 4
    add("licenses.overview", "GET", "/enterprises/ent-1/openapi/license/overview", lambda c: c.licenses.overview())
    add("licenses.query_members", "POST", "/enterprises/ent-1/openapi/license/members/query", lambda c: c.licenses.query_members(user_ids=["u1"], user_names=["alice"]), json_body={"userIds": ["u1"], "userNames": ["alice"]})
    add("licenses.grant", "POST", "/enterprises/ent-1/openapi/license/members/grant", lambda c: c.licenses.grant(user_ids=["u1"], user_names=["alice"]), json_body={"userIds": ["u1"], "userNames": ["alice"]})
    add("licenses.revoke", "POST", "/enterprises/ent-1/openapi/license/members/revoke", lambda c: c.licenses.revoke(user_ids=["u1"], reason="offboard"), json_body={"userIds": ["u1"], "reason": "offboard"})

    # usage 8
    add("usage.get_quota_cycle", "GET", "/enterprises/ent-1/openapi/usage/quota-cycle", lambda c: c.usage.get_quota_cycle())
    add("usage.get_default_quota", "GET", "/enterprises/ent-1/openapi/usage/default-quota", lambda c: c.usage.get_default_quota())
    add("usage.update_default_quota", "POST", "/enterprises/ent-1/openapi/usage/default-quota/update", lambda c: c.usage.update_default_quota(limit_type="limited", new_limit=100, cycle_type="MONTHLY"), json_body={"limitType": "limited", "newLimit": 100, "cycleType": "MONTHLY"})
    add("usage.query_members", "POST", "/enterprises/ent-1/openapi/usage/members/query", lambda c: c.usage.query_members(user_ids=["u1"], user_names=["alice"], page_num=1, page_size=20, start_time="2025-01-01", end_time="2025-01-02"), json_body={"userIds": ["u1"], "userNames": ["alice"], "pageNum": 1, "pageSize": 20, "startTime": "2025-01-01", "endTime": "2025-01-02"})
    add("usage.query_member_limits", "POST", "/enterprises/ent-1/openapi/usage/members/limit-query", lambda c: c.usage.query_member_limits(user_ids=["u1"], user_names=["alice"], page_num=1, page_size=20), json_body={"userIds": ["u1"], "userNames": ["alice"], "pageNum": 1, "pageSize": 20})
    add("usage.update_member_quota", "POST", "/enterprises/ent-1/openapi/usage/members/quota/update", lambda c: c.usage.update_member_quota(limit_type="limited", user_ids=["u1"], user_names=["alice"], new_limit=5000, cycle_type="MONTHLY"), json_body={"limitType": "limited", "userIds": ["u1"], "userNames": ["alice"], "newLimit": 5000, "cycleType": "MONTHLY"})
    add("usage.update_department_quota", "POST", "/enterprises/ent-1/openapi/usage/departments/d1/quota/update", lambda c: c.usage.update_department_quota("d1", limit_type="limited", new_limit=9, cycle_type="MONTHLY"), json_body={"limitType": "limited", "newLimit": 9, "cycleType": "MONTHLY"})
    add(
        "usage.query_member_details",
        "POST",
        "/enterprises/ent-1/openapi/usage/members/detail",
        lambda c: c.usage.query_member_details(
            time_range={"startTime": "2025-01-01T00:00:00+08:00", "endTime": "2025-01-02T00:00:00+08:00"},
            department_ids=["d1"],
            user_ids=["u1"],
            event_types=["chat.completion"],
            principal_types=["user"],
            page_num=1,
            version=2,
            page_token="",
            page_size=100,
            group_id="g1",
        ),
        json_body={
            "timeRange": {"startTime": "2025-01-01T00:00:00+08:00", "endTime": "2025-01-02T00:00:00+08:00"},
            "departmentIds": ["d1"],
            "userIds": ["u1"],
            "eventTypes": ["chat.completion"],
            "principalTypes": ["user"],
            "pageNum": 1,
            "pageSize": 100,
            "groupId": "g1",
            "version": 2,
            "pageToken": "",
        },
    )

    # groups 6
    add("groups.list", "GET", "/enterprises/ent-1/openapi/groups", lambda c: c.groups.list(page=1, page_size=20, keyword="team"), query={"page": "1", "pageSize": "20", "keyword": "team"})
    add("groups.get", "GET", "/enterprises/ent-1/openapi/groups/g1", lambda c: c.groups.get("g1"))
    add("groups.list_members", "GET", "/enterprises/ent-1/openapi/groups/g1/members", lambda c: c.groups.list_members("g1", page=1, page_size=10, keyword="alice"), query={"page": "1", "pageSize": "10", "keyword": "alice"})
    add("groups.add_members", "POST", "/enterprises/ent-1/openapi/groups/g1/members/add", lambda c: c.groups.add_members("g1", user_ids=["u1"], org_node_ids=["o1"]), json_body={"userIds": ["u1"], "orgNodeIds": ["o1"]})
    add("groups.remove_members", "POST", "/enterprises/ent-1/openapi/groups/g1/members/remove", lambda c: c.groups.remove_members("g1", user_ids=["u1"], org_node_ids=["o1"]), json_body={"userIds": ["u1"], "orgNodeIds": ["o1"]})
    add("groups.replace_members", "POST", "/enterprises/ent-1/openapi/groups/g1/members/replace", lambda c: c.groups.replace_members("g1", user_ids=["u1"], user_names=["alice"], clear_all=False), json_body={"userIds": ["u1"], "userNames": ["alice"], "clearAll": False})

    # models 13
    add("models.list_builtin", "GET", "/enterprises/ent-1/openapi/models/builtin", lambda c: c.models.list_builtin())
    add("models.set_builtin_enabled", "POST", "/enterprises/ent-1/openapi/models/builtin/m1/toggle", lambda c: c.models.set_builtin_enabled("m1", enabled=False), json_body={"enabled": False})
    add("models.set_builtin_visibility", "POST", "/enterprises/ent-1/openapi/models/builtin/m1/visibility", lambda c: c.models.set_builtin_visibility("m1", scope="specified", user_ids=["u1"], group_ids=["g1"]), json_body={"scope": "specified", "userIds": ["u1"], "groupIds": ["g1"]})
    add("models.list_custom", "GET", "/enterprises/ent-1/openapi/models/custom", lambda c: c.models.list_custom(page_num=1, page_size=20), query={"pageNum": "1", "pageSize": "20"})
    add(
        "models.create_custom",
        "POST",
        "/enterprises/ent-1/openapi/models/custom",
        lambda c: c.models.create_custom(
            display_name="N",
            provider="openai",
            base_url="https://api.example.test/v1",
            api_key="test-key",
            model_name="model-1",
            context_length=128000,
            enabled=True,
            scope="all",
            user_ids=["u1"],
            group_ids=["g1"],
        ),
        json_body={
            "displayName": "N",
            "provider": "openai",
            "baseUrl": "https://api.example.test/v1",
            "apiKey": "test-key",
            "modelName": "model-1",
            "contextLength": 128000,
            "enabled": True,
            "scope": "all",
            "userIds": ["u1"],
            "groupIds": ["g1"],
        },
    )
    add("models.get_custom", "GET", "/enterprises/ent-1/openapi/models/custom/m2", lambda c: c.models.get_custom("m2"))
    add("models.delete_custom", "POST", "/enterprises/ent-1/openapi/models/custom/m2/delete", lambda c: c.models.delete_custom("m2"), no_body=True)
    add("models.set_custom_visibility", "POST", "/enterprises/ent-1/openapi/models/custom/m2/visibility", lambda c: c.models.set_custom_visibility("m2", scope="specified", user_ids=["u1"], group_ids=["g1"]), json_body={"scope": "specified", "userIds": ["u1"], "groupIds": ["g1"]})
    add("models.list_available", "GET", "/enterprises/ent-1/openapi/models/available", lambda c: c.models.list_available(user_id="u1"), query={"userId": "u1"})
    add("models.list", "GET", "/enterprises/ent-1/openapi/models", lambda c: c.models.list(source="custom", page_num=1, page_size=10, enabled=True, provider="openai"), query={"source": "custom", "pageNum": "1", "pageSize": "10", "enabled": "true", "provider": "openai"})
    add("models.get", "GET", "/enterprises/ent-1/openapi/models/m3", lambda c: c.models.get("m3"))
    add("models.set_enabled", "POST", "/enterprises/ent-1/openapi/models/m3/toggle", lambda c: c.models.set_enabled("m3", enabled=True), json_body={"enabled": True})
    add("models.set_visibility", "POST", "/enterprises/ent-1/openapi/models/m3/visibility", lambda c: c.models.set_visibility("m3", scope="specified", user_ids=["u1"], group_ids=["g1"]), json_body={"scope": "specified", "userIds": ["u1"], "groupIds": ["g1"]})

    # skills 8
    add("skills.list", "GET", "/enterprises/ent-1/openapi/skills", lambda c: c.skills.list(source=SkillSource.CUSTOM, keyword="skill", category_id=1, publish_status="draft", page_num=1, page_size=20), query={"source": "custom", "keyword": "skill", "categoryId": "1", "publishStatus": "draft", "pageNum": "1", "pageSize": "20"})
    add("skills.create", "POST", "/enterprises/ent-1/openapi/skills", lambda c: c.skills.create(name="n", display_name="N", display_name_en="N", description_zh="zh", description_en="en", icon="icon", version="1.0.0", publish_status="draft", category_id=1, expected_md5="md5", expected_sha256="sha"), multipart=True)
    add("skills.get", "GET", "/enterprises/ent-1/openapi/skills/sk-1", lambda c: c.skills.get("sk-1"))
    add("skills.update", "POST", "/enterprises/ent-1/openapi/skills/sk-1/update", lambda c: c.skills.update("sk-1", name="n", display_name="N", display_name_en="N", description_zh="zh", description_en="en", icon="icon", version="1.1.0", publish_status="published", status="disabled", disabled_reason="reason", category_id=1, expected_md5="md5", expected_sha256="sha"), multipart=True)
    add("skills.delete", "POST", "/enterprises/ent-1/openapi/skills/sk-1/delete", lambda c: c.skills.delete("sk-1"), no_body=True)
    add("skills.set_enabled", "POST", "/enterprises/ent-1/openapi/skills/sk-1/toggle", lambda c: c.skills.set_enabled("sk-1", source="custom", enabled=False, disabled_reason="x"), query={"source": "custom"}, json_body={"enabled": False, "disabledReason": "x"})
    add("skills.set_visibility", "POST", "/enterprises/ent-1/openapi/skills/sk-1/visibility", lambda c: c.skills.set_visibility("sk-1", source="custom", type="scope_list", scopes=[{"scopeType": "user", "scopeId": "u1", "scopeName": "Alice"}]), query={"source": "custom"}, json_body={"type": "scope_list", "scopes": [{"scopeType": "user", "scopeId": "u1", "scopeName": "Alice"}]})
    add("skills.get_visibility", "GET", "/enterprises/ent-1/openapi/skills/sk-1/visibility", lambda c: c.skills.get_visibility("sk-1", source="custom"), query={"source": "custom"})

    # skill categories 5
    add("skill_categories.list", "GET", "/enterprises/ent-1/openapi/skill-categories", lambda c: c.skill_categories.list())
    add("skill_categories.create", "POST", "/enterprises/ent-1/openapi/skill-categories", lambda c: c.skill_categories.create(name="研发", description="desc", sort_order=1), json_body={"name": "研发", "description": "desc", "sortOrder": 1})
    add("skill_categories.update", "POST", "/enterprises/ent-1/openapi/skill-categories/10/update", lambda c: c.skill_categories.update(10, name="x", description="desc", sort_order=2), json_body={"name": "x", "description": "desc", "sortOrder": 2})
    add("skill_categories.delete", "POST", "/enterprises/ent-1/openapi/skill-categories/10/delete", lambda c: c.skill_categories.delete(10), no_body=True)
    add("skill_categories.reorder", "POST", "/enterprises/ent-1/openapi/skill-categories/reorder", lambda c: c.skill_categories.reorder([3, 1, 2]), json_body={"orderedIds": [3, 1, 2]})

    # experts 8
    add("experts.list", "GET", "/enterprises/ent-1/openapi/experts", lambda c: c.experts.list(source="custom", keyword="expert", category_id=1, publish_status="draft", page_num=1, page_size=20), query={"source": "custom", "keyword": "expert", "categoryId": "1", "publishStatus": "draft", "pageNum": "1", "pageSize": "20"})
    add("experts.create", "POST", "/enterprises/ent-1/openapi/experts", lambda c: c.experts.create(name="n", display_name="N", display_name_en="N", profession_zh="zh", profession_en="en", agent_name="agent", description_zh="zh", description_en="en", icon="icon", version="1.0.0", publish_status="draft", category_id=1, expected_md5="md5", expected_sha256="sha"), multipart=True)
    add("experts.get", "GET", "/enterprises/ent-1/openapi/experts/ex-1", lambda c: c.experts.get("ex-1"))
    add("experts.update", "POST", "/enterprises/ent-1/openapi/experts/ex-1/update", lambda c: c.experts.update("ex-1", name="n", display_name="N", display_name_en="N", profession_zh="zh", profession_en="en", agent_name="agent", description_zh="zh", description_en="en", icon="icon", version="1.0.1", publish_status="published", status="disabled", disabled_reason="reason", category_id=1, expected_md5="md5", expected_sha256="sha"), multipart=True)
    add("experts.delete", "POST", "/enterprises/ent-1/openapi/experts/ex-1/delete", lambda c: c.experts.delete("ex-1"), no_body=True)
    add("experts.set_enabled", "POST", "/enterprises/ent-1/openapi/experts/ex-1/toggle", lambda c: c.experts.set_enabled("ex-1", source="custom", enabled=False, disabled_reason="reason"), query={"source": "custom"}, json_body={"enabled": False, "disabledReason": "reason"})
    add("experts.set_visibility", "POST", "/enterprises/ent-1/openapi/experts/ex-1/visibility", lambda c: c.experts.set_visibility("ex-1", source="custom", type="scope_list", scopes=[{"scopeType": "user", "scopeId": "u1", "scopeName": "Alice"}]), query={"source": "custom"}, json_body={"type": "scope_list", "scopes": [{"scopeType": "user", "scopeId": "u1", "scopeName": "Alice"}]})
    add("experts.get_visibility", "GET", "/enterprises/ent-1/openapi/experts/ex-1/visibility", lambda c: c.experts.get_visibility("ex-1", source="custom"), query={"source": "custom"})

    # expert categories 5
    add("expert_categories.list", "GET", "/enterprises/ent-1/openapi/expert-categories", lambda c: c.expert_categories.list())
    add("expert_categories.create", "POST", "/enterprises/ent-1/openapi/expert-categories", lambda c: c.expert_categories.create(name="e", description="desc", sort_order=1), json_body={"name": "e", "description": "desc", "sortOrder": 1})
    add("expert_categories.update", "POST", "/enterprises/ent-1/openapi/expert-categories/2/update", lambda c: c.expert_categories.update(2, name="e", description="d", sort_order=2), json_body={"name": "e", "description": "d", "sortOrder": 2})
    add("expert_categories.delete", "POST", "/enterprises/ent-1/openapi/expert-categories/2/delete", lambda c: c.expert_categories.delete(2), no_body=True)
    add("expert_categories.reorder", "POST", "/enterprises/ent-1/openapi/expert-categories/reorder", lambda c: c.expert_categories.reorder([1, 2]), json_body={"orderedIds": [1, 2]})

    # analytics 8
    add("analytics.metrics_download_url_v2", "GET", "/enterprises/ent-1/metrics/download_url/v2", lambda c: c.analytics.metrics_download_url_v2(queries="q1", range_start="2025-03-20 00:00:00", range_end="2025-03-20 00:00:00", range_step=86400), query={"queries": "q1", "range.start": "2025-03-20 00:00:00", "range.end": "2025-03-20 00:00:00", "range.step": "86400"})
    add("analytics.metrics_download_url", "GET", "/enterprises/ent-1/metrics/download_url", lambda c: c.analytics.metrics_download_url(queries="q1", range_start="2025-03-20 00:00:00", range_end="2025-03-20 00:00:00", range_step=86400), query={"queries": "q1", "range.start": "2025-03-20 00:00:00", "range.end": "2025-03-20 00:00:00", "range.step": "86400"})
    add("analytics.metrics", "GET", "/enterprises/ent-1/metrics", lambda c: c.analytics.metrics(queries="q1", range_start="2025-03-20 00:00:00", range_end="2025-03-20 00:00:00", range_step=86400), query={"queries": "q1", "range.start": "2025-03-20 00:00:00", "range.end": "2025-03-20 00:00:00", "range.step": "86400"})
    activity_body = {
        **dashboard_filters,
        "viewType": "metrics",
        "activityOptions": {"distributionDimension": "none"},
    }
    dialog_body = {
        **dashboard_filters,
        "viewType": "metrics",
        "dialogOptions": {"distributionDimension": "clientName", "abilities": {"type": "all", "data": []}, "models": {"type": "all", "data": []}},
    }
    completion_body = {
        **dashboard_filters,
        "viewType": "metrics",
        "completionOptions": {"languageFilter": {"type": "all", "data": []}, "models": {"type": "all", "data": []}, "distributionDimension": "clientName", "statisticsType": "count"},
    }
    generation_body = {
        **dashboard_filters,
        "viewType": "metrics",
        "generationOptions": {"distributionDimension": "clientName", "statisticsType": "line", "languageFilter": {"type": "all", "data": []}},
    }
    member_data_body = {
        **dashboard_filters,
        "pagination": {"page": 1, "pageSize": 20},
        "memberOptions": {"sortBy": "memberName", "sortOrder": "asc", "searchKeyword": "alice"},
    }
    add("analytics.activity", "POST", "/enterprises/ent-1/dashboard/analytics/activity", lambda c: c.analytics.activity(activity_body), json_body=activity_body)
    add("analytics.dialog", "POST", "/enterprises/ent-1/dashboard/analytics/dialog", lambda c: c.analytics.dialog(dialog_body), json_body=dialog_body)
    add("analytics.completion", "POST", "/enterprises/ent-1/dashboard/analytics/completion", lambda c: c.analytics.completion(completion_body), json_body=completion_body)
    add("analytics.generation", "POST", "/enterprises/ent-1/dashboard/analytics/generation", lambda c: c.analytics.generation(generation_body), json_body=generation_body)
    add("analytics.member_data", "POST", "/enterprises/ent-1/dashboard/member/data", lambda c: c.analytics.member_data(member_data_body), json_body=member_data_body)

    return cases


CASES = _cases()


def _load_openapi_spec() -> Mapping[str, Any] | None:
    candidates: list[Path] = []
    configured = os.environ.get("WORKBUDDY_OPENAPI_SPEC")
    if configured:
        candidates.append(Path(configured))
    candidates.append(Path(__file__).resolve().parents[5] / "local" / "codebuddy-openapi-api.yaml")
    for candidate in candidates:
        if candidate.is_file():
            with candidate.open(encoding="utf-8") as fh:
                document = yaml.safe_load(fh)
            if isinstance(document, Mapping):
                return document
    return None


@pytest.fixture(scope="module")
def openapi_spec() -> Mapping[str, Any] | None:
    return _load_openapi_spec()


def _path_matches(template: str, concrete: str) -> bool:
    template_parts = template.strip("/").split("/")
    concrete_parts = concrete.strip("/").split("/")
    return len(template_parts) == len(concrete_parts) and all(
        (part.startswith("{") and part.endswith("}")) or part == value
        for part, value in zip(template_parts, concrete_parts)
    )


def _operation_for_case(
    spec: Mapping[str, Any], method: str, suffix: str,
) -> tuple[str, Mapping[str, Any]]:
    matches: list[tuple[str, Mapping[str, Any]]] = []
    for path, path_item in spec.get("paths", {}).items():
        operation = path_item.get(method.lower())
        if operation is not None and _path_matches(path, suffix):
            matches.append((path, operation))
    assert matches, f"no OpenAPI operation matches {method} {suffix}"
    def specificity(item: tuple[str, Mapping[str, Any]]) -> int:
        return sum(
            not (part.startswith("{") and part.endswith("}"))
            for part in item[0].strip("/").split("/")
        )
    best_score = max(specificity(match) for match in matches)
    best_matches = [match for match in matches if specificity(match) == best_score]
    assert len(best_matches) == 1, f"ambiguous OpenAPI operation for {method} {suffix}: {best_matches!r}"
    return best_matches[0]


def _required_query(operation: Mapping[str, Any], path_item: Mapping[str, Any]) -> set[str]:
    parameters = [*path_item.get("parameters", []), *operation.get("parameters", [])]
    return {
        parameter["name"]
        for parameter in parameters
        if parameter.get("in") == "query" and parameter.get("required")
    }


def _resolve_schema(spec: Mapping[str, Any], schema: Mapping[str, Any]) -> Mapping[str, Any]:
    ref = schema.get("$ref")
    if not ref:
        return schema
    prefix = "#/components/schemas/"
    assert ref.startswith(prefix), f"unsupported schema reference: {ref}"
    return spec["components"]["schemas"][ref.removeprefix(prefix)]


def _undeclared_object_fields(fields: set[str], schema: Mapping[str, Any]) -> set[str]:
    properties = schema.get("properties")
    declared = set(properties) if isinstance(properties, Mapping) else set()
    undeclared = fields - declared
    additional_properties = schema.get("additionalProperties", _ADDITIONAL_PROPERTIES_UNSET)
    if additional_properties is True or isinstance(additional_properties, Mapping):
        return set()
    if additional_properties is _ADDITIONAL_PROPERTIES_UNSET and not declared:
        return set()
    return undeclared


def _assert_schema_value(spec: Mapping[str, Any], value: Any, schema: Mapping[str, Any], label: str) -> None:
    schema = _resolve_schema(spec, schema)
    expected_type = schema.get("type")
    if expected_type == "object":
        assert isinstance(value, Mapping), f"{label} must be an object"
    elif expected_type == "array":
        assert isinstance(value, list), f"{label} must be an array"
    elif expected_type == "string":
        assert isinstance(value, str), f"{label} must be a string"
    elif expected_type == "integer":
        assert isinstance(value, int) and not isinstance(value, bool), f"{label} must be an integer"
    elif expected_type == "number":
        assert isinstance(value, (int, float)) and not isinstance(value, bool), f"{label} must be a number"
    elif expected_type == "boolean":
        assert isinstance(value, bool), f"{label} must be a boolean"
    if "enum" in schema:
        assert value in schema["enum"], f"{label}={value!r} is not in {schema['enum']!r}"
    if isinstance(value, Mapping):
        required = set(schema.get("required", []))
        assert required <= set(value), f"{label} missing required fields: {sorted(required - set(value))}"
        declared = set(schema.get("properties", {}))
        assert declared <= set(value), f"{label} fields not expressed by case: {sorted(declared - set(value))}"
        undeclared = _undeclared_object_fields(set(value), schema)
        assert not undeclared, f"{label} has undeclared fields: {sorted(undeclared)}"
        for key, nested_schema in schema.get("properties", {}).items():
            if key in value:
                _assert_schema_value(spec, value[key], nested_schema, f"{label}.{key}")
        additional_properties = schema.get("additionalProperties")
        if isinstance(additional_properties, Mapping):
            for key in set(value) - declared:
                _assert_schema_value(spec, value[key], additional_properties, f"{label}.{key}")
    elif isinstance(value, list) and "items" in schema:
        for index, item in enumerate(value):
            _assert_schema_value(spec, item, schema["items"], f"{label}[{index}]")


def _multipart_field_names(content: bytes) -> set[str]:
    import re

    return {
        match.decode("utf-8")
        for match in re.findall(
            br'(?im)^Content-Disposition:\s*form-data;\s*name="([^"]+)"',
            content,
        )
    }


def _assert_openapi_request_contract(
    req: httpx.Request,
    operation: Mapping[str, Any],
    path_item: Mapping[str, Any],
    spec: Mapping[str, Any],
) -> None:
    parameters = [*path_item.get("parameters", []), *operation.get("parameters", [])]
    missing_query = _required_query(operation, path_item) - set(req.url.params.keys())
    assert not missing_query, f"missing required query parameters: {sorted(missing_query)}"
    declared_query = {parameter["name"] for parameter in parameters if parameter.get("in") == "query"}
    undeclared_query = set(req.url.params.keys()) - declared_query
    assert not undeclared_query, f"undeclared query parameters: {sorted(undeclared_query)}"
    assert declared_query <= set(req.url.params.keys()), (
        f"query fields not expressed by case: {sorted(declared_query - set(req.url.params.keys()))}"
    )
    for parameter in parameters:
        name = parameter.get("name")
        if parameter.get("in") == "query" and name in req.url.params:
            schema = _resolve_schema(spec, parameter.get("schema", {}))
            if "enum" in schema:
                assert req.url.params[name] in {str(value) for value in schema["enum"]}, (
                    f"query.{name}={req.url.params[name]!r} is not in {schema['enum']!r}"
                )

    request_body = operation.get("requestBody")
    if request_body is None:
        assert req.content == b""
        assert "content-type" not in req.headers
        return

    content = request_body.get("content", {})
    media_type = req.headers.get("content-type", "").split(";", 1)[0]
    assert media_type in content, f"unexpected content type {media_type!r}; expected one of {sorted(content)}"
    schema = _resolve_schema(spec, content[media_type].get("schema", {}))
    required = set(schema.get("required", []))
    if media_type == "application/json":
        body = json.loads(req.content.decode())
        assert required <= set(body), f"missing required body fields: {sorted(required - set(body))}"
        declared = set(schema.get("properties", {}))
        assert declared <= set(body), f"body fields not expressed by case: {sorted(declared - set(body))}"
        _assert_schema_value(spec, body, schema, "body")
    elif media_type == "multipart/form-data":
        fields = _multipart_field_names(req.content)
        assert required <= fields, f"missing required multipart fields: {sorted(required - fields)}"
        undeclared = _undeclared_object_fields(fields, schema)
        assert not undeclared, f"multipart has undeclared fields: {sorted(undeclared)}"
        declared = set(schema.get("properties", {})) - {"package"}
        assert declared <= fields, f"multipart fields not expressed by case: {sorted(declared - fields)}"


def test_cases_match_current_openapi_operation_set(openapi_spec):
    if openapi_spec is None:
        pytest.skip(
            "OpenAPI spec not found; set WORKBUDDY_OPENAPI_SPEC or provide "
            "local/codebuddy-openapi-api.yaml",
        )
    case_operations = {
        (method, _operation_for_case(openapi_spec, method, suffix)[0])
        for _, method, suffix, _, _ in CASES
    }
    spec_operations = {
        (method.upper(), path)
        for path, path_item in openapi_spec.get("paths", {}).items()
        for method in path_item
        if method.lower() in HTTP_METHODS
    }
    assert case_operations == spec_operations


@pytest.mark.parametrize("op_id,method,suffix,invoker,expect", CASES, ids=[c[0] for c in CASES])
def test_operation_contract(op_id, method, suffix, invoker, expect, openapi_spec):
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
        no_body=bool(expect.get("no_body")),
    )
    if openapi_spec is not None:
        path, operation = _operation_for_case(openapi_spec, method, suffix)
        _assert_openapi_request_contract(req, operation, openapi_spec["paths"][path], openapi_spec)
    # auth header present and not logging secrets elsewhere
    assert req.headers.get("Authorization") == "Bearer t"


def test_operation_count_is_73():
    assert len(CASES) == 73


@pytest.fixture
def minimal_request_spec() -> dict[str, Any]:
    return {"components": {"schemas": {}}}


def test_request_contract_rejects_undeclared_query_parameter(minimal_request_spec):
    request = httpx.Request("GET", "https://example.test/items?known=ok&bogus=extra")
    operation = {
        "parameters": [
            {"in": "query", "name": "known", "schema": {"type": "string"}},
        ],
    }

    with pytest.raises(AssertionError, match=r"undeclared query parameters: \['bogus'\]"):
        _assert_openapi_request_contract(request, operation, {}, minimal_request_spec)


def test_request_contract_rejects_undeclared_json_field(minimal_request_spec):
    request = httpx.Request(
        "POST",
        "https://example.test/items",
        json={"known": "ok", "bogus": "extra"},
    )
    operation = {
        "requestBody": {
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {"known": {"type": "string"}},
                    },
                },
            },
        },
    }

    with pytest.raises(AssertionError, match=r"body has undeclared fields: \['bogus'\]"):
        _assert_openapi_request_contract(request, operation, {}, minimal_request_spec)


def test_request_contract_rejects_undeclared_multipart_field(minimal_request_spec):
    boundary = "workbuddy-contract-boundary"
    content = (
        f'--{boundary}\r\nContent-Disposition: form-data; name="known"\r\n\r\nok\r\n'
        f'--{boundary}\r\nContent-Disposition: form-data; name="bogus"\r\n\r\nextra\r\n'
        f"--{boundary}--\r\n"
    ).encode()
    request = httpx.Request(
        "POST",
        "https://example.test/items",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        content=content,
    )
    operation = {
        "requestBody": {
            "content": {
                "multipart/form-data": {
                    "schema": {
                        "type": "object",
                        "properties": {"known": {"type": "string"}},
                    },
                },
            },
        },
    }

    with pytest.raises(AssertionError, match=r"multipart has undeclared fields: \['bogus'\]"):
        _assert_openapi_request_contract(request, operation, {}, minimal_request_spec)


def test_object_schema_without_properties_remains_free_form(minimal_request_spec):
    _assert_schema_value(
        minimal_request_spec,
        {"dynamic": "value"},
        {"type": "object"},
        "body",
    )


@pytest.mark.parametrize("additional_properties", [True, {"type": "integer"}])
def test_explicit_additional_properties_allow_dynamic_fields(
    minimal_request_spec,
    additional_properties,
):
    _assert_schema_value(
        minimal_request_spec,
        {"known": "ok", "dynamic": 1},
        {
            "type": "object",
            "properties": {"known": {"type": "string"}},
            "additionalProperties": additional_properties,
        },
        "body",
    )


def test_additional_properties_schema_validates_dynamic_values(minimal_request_spec):
    schema = {
        "type": "object",
        "properties": {"known": {"type": "string"}},
        "additionalProperties": {"type": "integer"},
    }

    with pytest.raises(AssertionError, match="body.dynamic must be an integer"):
        _assert_schema_value(
            minimal_request_spec,
            {"known": "ok", "dynamic": "not-an-integer"},
            schema,
            "body",
        )
