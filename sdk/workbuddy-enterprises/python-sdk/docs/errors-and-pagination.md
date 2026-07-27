# Errors and pagination

## Errors

| Exception | When |
|---|---|
| `WorkBuddyConfigError` | Invalid local configuration |
| `WorkBuddyAuthError` | Token acquisition failed |
| `WorkBuddyHTTPError` | HTTP status >= 400 |
| `WorkBuddyAPIError` | HTTP 2xx and business `code != 0` |
| `WorkBuddyTimeoutError` | Timeout / transport timeout |

Fields commonly available: `http_status`, `code`, `message`/`request_id` via attributes.

## Pagination styles

1. `page` + `pageSize`
2. `pageNum` + `pageSize`
3. Usage detail v2: `version=2` + `pageToken` / `nextPageToken`

List responses are normalized into `Page` when the payload contains `items` / `list`.
