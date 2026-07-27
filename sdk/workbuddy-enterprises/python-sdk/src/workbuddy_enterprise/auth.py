
"""Authentication helpers."""

from __future__ import annotations

import base64
import json
import os
import time
from dataclasses import dataclass
from typing import Any, Mapping

import httpx

from workbuddy_enterprise.errors import WorkBuddyAuthError, WorkBuddyConfigError

DEFAULT_BASE_URL = "https://api.copilot.tencent.com/api/v1"
DEFAULT_TOKEN_URL = "https://copilot.tencent.com/oauth2/token"

ENV_ENTERPRISE_ID = "WORKBUDDY_ENTERPRISE_ID"
ENV_CLIENT_ID = "WORKBUDDY_CLIENT_ID"
ENV_CLIENT_SECRET = "WORKBUDDY_CLIENT_SECRET"
ENV_API_KEY = "WORKBUDDY_API_KEY"
ENV_BASE_URL = "WORKBUDDY_BASE_URL"
ENV_TOKEN_URL = "WORKBUDDY_TOKEN_URL"


@dataclass(slots=True)
class AuthConfig:
    enterprise_id: str
    client_id: str | None = None
    client_secret: str | None = None
    api_key: str | None = None
    base_url: str = DEFAULT_BASE_URL
    token_url: str = DEFAULT_TOKEN_URL

    def validate(self) -> None:
        if not self.enterprise_id:
            raise WorkBuddyConfigError(
                f"enterprise_id is required (set {ENV_ENTERPRISE_ID} or pass enterprise_id=...)"
            )
        has_oauth = bool(self.client_id and self.client_secret)
        has_key = bool(self.api_key)
        if has_oauth and has_key:
            raise WorkBuddyConfigError(
                "Provide either OAuth client credentials or api_key, not both"
            )
        if not has_oauth and not has_key:
            raise WorkBuddyConfigError(
                "Provide OAuth client_id/client_secret or enterprise api_key (pt_...)"
            )
        if has_oauth and (not self.client_id or not self.client_secret):
            raise WorkBuddyConfigError("OAuth requires both client_id and client_secret")


def auth_config_from_env(
    *,
    environ: Mapping[str, str] | None = None,
    enterprise_id: str | None = None,
    client_id: str | None = None,
    client_secret: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
    token_url: str | None = None,
) -> AuthConfig:
    env = environ if environ is not None else os.environ
    cfg = AuthConfig(
        enterprise_id=(enterprise_id or env.get(ENV_ENTERPRISE_ID) or "").strip(),
        client_id=(client_id if client_id is not None else env.get(ENV_CLIENT_ID)),
        client_secret=(
            client_secret if client_secret is not None else env.get(ENV_CLIENT_SECRET)
        ),
        api_key=(api_key if api_key is not None else env.get(ENV_API_KEY)),
        base_url=(base_url or env.get(ENV_BASE_URL) or DEFAULT_BASE_URL).rstrip("/"),
        token_url=(token_url or env.get(ENV_TOKEN_URL) or DEFAULT_TOKEN_URL),
    )
    # normalize empty strings to None for optional secrets
    if cfg.client_id == "":
        cfg.client_id = None
    if cfg.client_secret == "":
        cfg.client_secret = None
    if cfg.api_key == "":
        cfg.api_key = None
    cfg.validate()
    return cfg


def b64url_json(segment: str) -> dict[str, Any]:
    pad = "=" * ((4 - len(segment) % 4) % 4)
    return json.loads(base64.urlsafe_b64decode(segment + pad).decode("utf-8"))


def decode_jwt_payload(token: str) -> dict[str, Any] | None:
    parts = token.split(".")
    if len(parts) < 2:
        return None
    try:
        return b64url_json(parts[1])
    except Exception:
        return None


def extract_enterprise_ids_from_token(token: str) -> list[str]:
    """Opt-in helper: parse ent-member:{id} roles from a JWT access token."""
    payload = decode_jwt_payload(token) or {}
    roles = (
        (payload.get("realm_access") or {}).get("roles")
        or payload.get("roles")
        or []
    )
    ids: list[str] = []
    for role in roles:
        if isinstance(role, str) and role.startswith("ent-member:"):
            ent = role.split(":", 1)[1].strip()
            if ent and ent not in ids:
                ids.append(ent)
    return ids


class TokenProvider:
    def __init__(
        self,
        config: AuthConfig,
        *,
        http_client: httpx.Client | None = None,
        owns_client: bool = False,
    ) -> None:
        self._config = config
        self._http = http_client or httpx.Client(timeout=30.0)
        self._owns_client = owns_client or http_client is None
        self._access_token: str | None = None
        self._expires_at: float = 0.0

    def close(self) -> None:
        if self._owns_client:
            self._http.close()

    def get_token(self, *, force_refresh: bool = False) -> str:
        if self._config.api_key:
            return self._config.api_key
        now = time.time()
        if (
            not force_refresh
            and self._access_token
            and now < self._expires_at - 30
        ):
            return self._access_token
        assert self._config.client_id and self._config.client_secret
        try:
            resp = self._http.post(
                self._config.token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self._config.client_id,
                    "client_secret": self._config.client_secret,
                },
                headers={"Accept": "application/json"},
            )
        except httpx.TimeoutException as exc:
            raise WorkBuddyAuthError("Timed out while requesting access_token") from exc
        except httpx.HTTPError as exc:
            raise WorkBuddyAuthError(f"Failed to request access_token: {exc}") from exc

        try:
            body = resp.json()
        except Exception:
            body = {"raw": resp.text[:200]}

        if resp.status_code >= 400 or not isinstance(body, dict) or not body.get("access_token"):
            raise WorkBuddyAuthError(
                "Failed to obtain access_token",
                http_status=resp.status_code,
                details={"error": body.get("error") if isinstance(body, dict) else None},
            )
        self._access_token = str(body["access_token"])
        expires_in = body.get("expires_in")
        try:
            ttl = float(expires_in) if expires_in is not None else 3600.0
        except (TypeError, ValueError):
            ttl = 3600.0
        self._expires_at = time.time() + ttl
        return self._access_token
