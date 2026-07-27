
"""Root synchronous client."""

from __future__ import annotations

from typing import Any

import httpx

from workbuddy_enterprise.auth import (
    DEFAULT_BASE_URL,
    DEFAULT_TOKEN_URL,
    AuthConfig,
    auth_config_from_env,
)
from workbuddy_enterprise._transport import Transport
from workbuddy_enterprise.resources.analytics import AnalyticsResource
from workbuddy_enterprise.resources.enterprise import EnterpriseResource
from workbuddy_enterprise.resources.expert_categories import ExpertCategoriesResource
from workbuddy_enterprise.resources.experts import ExpertsResource
from workbuddy_enterprise.resources.groups import GroupsResource
from workbuddy_enterprise.resources.licenses import LicensesResource
from workbuddy_enterprise.resources.members import MembersResource
from workbuddy_enterprise.resources.models import ModelsResource
from workbuddy_enterprise.resources.skill_categories import SkillCategoriesResource
from workbuddy_enterprise.resources.skills import SkillsResource
from workbuddy_enterprise.resources.usage import UsageResource
from workbuddy_enterprise.resources.users import UsersResource


class WorkBuddyClient:
    """Unofficial synchronous client for CodeBuddy / WorkBuddy Enterprise OpenAPI."""

    def __init__(
        self,
        config: AuthConfig,
        *,
        timeout: float | httpx.Timeout = 30.0,
        transport: httpx.BaseTransport | None = None,
        http_client: httpx.Client | None = None,
        max_read_retries: int = 2,
    ) -> None:
        config.validate()
        self._config = config
        self._transport = Transport(
            config,
            timeout=timeout,
            transport=transport,
            client=http_client,
            max_read_retries=max_read_retries,
        )
        self.enterprise = EnterpriseResource(self._transport)
        self.users = UsersResource(self._transport)
        self.members = MembersResource(self._transport)
        self.licenses = LicensesResource(self._transport)
        self.usage = UsageResource(self._transport)
        self.groups = GroupsResource(self._transport)
        self.models = ModelsResource(self._transport)
        self.skills = SkillsResource(self._transport)
        self.skill_categories = SkillCategoriesResource(self._transport)
        self.experts = ExpertsResource(self._transport)
        self.expert_categories = ExpertCategoriesResource(self._transport)
        self.analytics = AnalyticsResource(self._transport)

    @property
    def enterprise_id(self) -> str:
        return self._config.enterprise_id

    @property
    def base_url(self) -> str:
        return self._config.base_url

    @classmethod
    def from_client_credentials(
        cls,
        *,
        client_id: str,
        client_secret: str,
        enterprise_id: str,
        base_url: str = DEFAULT_BASE_URL,
        token_url: str = DEFAULT_TOKEN_URL,
        **kwargs: Any,
    ) -> "WorkBuddyClient":
        cfg = AuthConfig(
            enterprise_id=enterprise_id,
            client_id=client_id,
            client_secret=client_secret,
            base_url=base_url.rstrip("/"),
            token_url=token_url,
        )
        return cls(cfg, **kwargs)

    @classmethod
    def from_api_key(
        cls,
        *,
        api_key: str,
        enterprise_id: str,
        base_url: str = DEFAULT_BASE_URL,
        **kwargs: Any,
    ) -> "WorkBuddyClient":
        cfg = AuthConfig(
            enterprise_id=enterprise_id,
            api_key=api_key,
            base_url=base_url.rstrip("/"),
        )
        return cls(cfg, **kwargs)

    @classmethod
    def from_env(cls, **overrides: Any) -> "WorkBuddyClient":
        timeout = overrides.pop("timeout", 30.0)
        transport = overrides.pop("transport", None)
        http_client = overrides.pop("http_client", None)
        max_read_retries = overrides.pop("max_read_retries", 2)
        cfg = auth_config_from_env(**overrides)
        return cls(
            cfg,
            timeout=timeout,
            transport=transport,
            http_client=http_client,
            max_read_retries=max_read_retries,
        )

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> "WorkBuddyClient":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
