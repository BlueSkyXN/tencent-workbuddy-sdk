
import pytest

from workbuddy_enterprise.auth import AuthConfig, auth_config_from_env
from workbuddy_enterprise.errors import WorkBuddyConfigError


def test_rejects_both_oauth_and_api_key():
    with pytest.raises(WorkBuddyConfigError):
        AuthConfig(
            enterprise_id="e1",
            client_id="c",
            client_secret="s",
            api_key="pt_x",
        ).validate()


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
