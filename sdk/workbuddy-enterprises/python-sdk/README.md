# workbuddy-enterprise (Python)

> 仓库总文档：[docs/README.md](../../../docs/README.md) · 快速开始：[docs/getting-started.md](../../../docs/getting-started.md)


**Unofficial** synchronous Python SDK for the CodeBuddy / WorkBuddy **Enterprise OpenAPI**.

> This is **not** an official Tencent / CodeBuddy package.
> It wraps the public Enterprise OpenAPI (`api.yaml`), not the Agent Runtime SDK or Managed Agents / AgentOS SDK.

| Item | Value |
|---|---|
| Repo path | `sdk/workbuddy-enterprises/python-sdk` |
| Distribution | `workbuddy-enterprise` |
| Import | `workbuddy_enterprise` |
| Root client | `WorkBuddyClient` |
| Runtime | sync only (`httpx`) |
| License | GPL-3.0 (see `LICENSE`) |

## Scope

Covers the enterprise management OpenAPI surface, including:

- enterprise / users
- members / licenses
- usage
- groups
- models
- skills / skill categories
- experts / expert categories
- metrics / dashboard analytics

**Not in scope:** CLI, async client, UI/service, scheduler, approval workflow, auto publish/unpublish product logic.

## Spec anchor

**权威来源（官方）：** https://www.codebuddy.cn/apiDocs/api.yaml

人读文档站：https://www.codebuddy.cn/apiDocs/index.html

仓库级说明：[docs/openapi-spec.md](../../../docs/openapi-spec.md)

Public docs:

- UI: https://www.codebuddy.cn/apiDocs/index.html
- OpenAPI: https://www.codebuddy.cn/apiDocs/api.yaml
- Base URL default: `https://api.copilot.tencent.com/api/v1`
- Token URL default: `https://copilot.tencent.com/oauth2/token`

Local snapshot used while implementing (repo-root, not committed):

| Field | Value |
|---|---|
| Path | `local/codebuddy-openapi-api.yaml` (gitignored, repo root) |
| Captured | 2026-07-27 |
| Lines / bytes | 5,597 / 238,561 |
| SHA-256 | `e6c6e6f8c350a4219a45f1b6d488d4b38d29c3e2a872d4b1b31c46774b0638fe` |
| Paths / operations | 66 / 73 |

```bash
python tools/inventory_openapi.py ../../../local/codebuddy-openapi-api.yaml
```

## Install

From this directory:

```bash
python -m pip install -e ".[dev]"
```

## Auth

Enterprise application identity only (not personal API keys for admin APIs).

```text
WORKBUDDY_ENTERPRISE_ID=...
WORKBUDDY_CLIENT_ID=...
WORKBUDDY_CLIENT_SECRET=...
# or
WORKBUDDY_API_KEY=pt_...

# optional
WORKBUDDY_BASE_URL=https://api.copilot.tencent.com/api/v1
WORKBUDDY_TOKEN_URL=https://copilot.tencent.com/oauth2/token
```

Provide **either** OAuth client credentials **or** `pt_` API key, not both.

## Quick example

```python
from workbuddy_enterprise import WorkBuddyClient
from workbuddy_enterprise.types import SkillSource

with WorkBuddyClient.from_client_credentials(
    client_id="...",
    client_secret="...",
    enterprise_id="...",
) as workbuddy:
    resp = workbuddy.skills.list(source=SkillSource.CUSTOM)
    for skill in resp.data.items:
        print(skill.name, skill.version, skill.enabled)
```

See `examples/`.

## Testing

```bash
python -m pytest tests/unit tests/contract
```

Live read-only (optional):

```bash
export WORKBUDDY_LIVE=1
python -m pytest tests/live -m live
```

Coverage matrix: [`docs/api-coverage.md`](docs/api-coverage.md)

## CI / packaging

GitHub Actions builds from this package directory and uploads sdist/wheel artifacts.
No PyPI publish is configured.

## Repository constraint

本仓库要求减少本机磁盘压力；打包优先 CI。详见：

[`docs/local-disk-and-ci-builds.md`](../../../docs/local-disk-and-ci-builds.md)

