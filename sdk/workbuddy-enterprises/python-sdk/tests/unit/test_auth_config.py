
import base64
import json

import pytest

from workbuddy_enterprise.auth import (
    AuthConfig,
    auth_config_from_env,
    extract_enterprise_ids_from_token,
)
from workbuddy_enterprise.errors import WorkBuddyConfigError


def test_rejects_both_oauth_and_api_key():
    with pytest.raises(WorkBuddyConfigError):
        AuthConfig(
            enterprise_id="e1",
            client_id="c",
            client_secret="s",
            api_key="pt_x",
        ).validate()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"client_id": "c"},
        {"client_secret": "s"},
        {"client_id": "c", "api_key": "pt_x"},
        {"client_secret": "s", "api_key": "pt_x"},
        {"client_id": "", "api_key": "pt_x"},
        {"client_secret": "", "api_key": "pt_x"},
        {"client_id": "c", "client_secret": "s", "api_key": "pt_x"},
    ],
)
def test_rejects_partial_or_mixed_auth_config(kwargs):
    with pytest.raises(WorkBuddyConfigError):
        AuthConfig(enterprise_id="e1", **kwargs).validate()


@pytest.mark.parametrize("oauth_name", ["WORKBUDDY_CLIENT_ID", "WORKBUDDY_CLIENT_SECRET"])
def test_env_rejects_empty_oauth_field_mixed_with_api_key(oauth_name):
    with pytest.raises(WorkBuddyConfigError):
        auth_config_from_env(
            environ={
                "WORKBUDDY_ENTERPRISE_ID": "e1",
                "WORKBUDDY_API_KEY": "pt_x",
                oauth_name: "",
            },
        )


def test_requires_enterprise_id():
    with pytest.raises(WorkBuddyConfigError):
        AuthConfig(enterprise_id="", client_id="c", client_secret="s").validate()


def test_from_env_oauth(monkeypatch):
    monkeypatch.setenv("WORKBUDDY_ENTERPRISE_ID", "ent")
    monkeypatch.setenv("WORKBUDDY_CLIENT_ID", "cid")
    monkeypatch.setenv("WORKBUDDY_CLIENT_SECRET", "sec")
    monkeypatch.delenv("WORKBUDDY_API_KEY", raising=False)
    cfg = auth_config_from_env()
    assert cfg.enterprise_id == "ent"
    assert cfg.client_id == "cid"
    assert cfg.api_key is None


def test_error_str_does_not_include_secret():
    err = WorkBuddyConfigError("bad config with no secret leakage")
    assert "csecret" not in str(err)


def _unsigned_token(payload) -> str:
    encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=").decode()
    return f"header.{encoded}.signature"


@pytest.mark.parametrize("payload", [[1], "text", 1])
def test_extract_enterprise_ids_rejects_non_object_payload(payload):
    assert extract_enterprise_ids_from_token(_unsigned_token(payload)) == []


@pytest.mark.parametrize("realm_access", ["invalid", [1], 1])
def test_extract_enterprise_ids_rejects_non_object_realm_access(realm_access):
    assert extract_enterprise_ids_from_token(
        _unsigned_token({"realm_access": realm_access}),
    ) == []


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        ({"realm_access": {"roles": ["other", "ent-member:e1", "ent-member:e1"]}}, ["e1"]),
        ({"roles": ["ent-member:e2"]}, ["e2"]),
    ],
)
def test_extract_enterprise_ids_accepts_supported_role_shapes(payload, expected):
    assert extract_enterprise_ids_from_token(_unsigned_token(payload)) == expected
