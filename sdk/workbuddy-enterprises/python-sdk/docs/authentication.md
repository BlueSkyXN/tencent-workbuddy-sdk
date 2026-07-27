# Authentication

## Supported modes

1. OAuth2 `client_credentials` (`WORKBUDDY_CLIENT_ID` + `WORKBUDDY_CLIENT_SECRET`)
2. Enterprise application API key (`WORKBUDDY_API_KEY`, typically `pt_...`)

If both are provided, the SDK raises `WorkBuddyConfigError`.

## Required enterprise id

`WORKBUDDY_ENTERPRISE_ID` (or constructor `enterprise_id=...`) is required.

Do not rely on JWT parsing for production configuration. The helper `extract_enterprise_ids_from_token` is opt-in only.

## Endpoints

| Setting | Default |
|---|---|
| `base_url` | `https://api.copilot.tencent.com/api/v1` |
| `token_url` | `https://copilot.tencent.com/oauth2/token` |

Exclusive / private deployments should override both as needed.
