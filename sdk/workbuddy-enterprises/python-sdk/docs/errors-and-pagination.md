# Errors and pagination

## Errors

| Exception | When |
|---|---|
| `WorkBuddyConfigError` | Invalid local configuration |
| `WorkBuddyAuthError` | Token acquisition failed |
| `WorkBuddyHTTPError` | HTTP status >= 400, or a non-timeout transport failure after read retries (`http_status=0`) |
| `WorkBuddyAPIError` | HTTP 2xx and business `code != 0` |
| `WorkBuddyTimeoutError` | Timeout after read retries |

Fields commonly available: `http_status`, `code`, `message`/`request_id` via attributes.

GET/HEAD requests retry timeout and transport failures according to `max_read_retries` (default: 2
retries after the first attempt). Mutating requests are not retried automatically.

## Pagination styles

1. `page` + `pageSize`
2. `pageNum` + `pageSize`
3. Usage detail v2: `version=2` + `pageToken` / `nextPageToken`

List responses are normalized into `Page` when the payload contains `items` / `list`.
