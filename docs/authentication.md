# 鉴权说明（仓库级）

更细的 Python 包说明见：  
[`../sdk/workbuddy-enterprises/python-sdk/docs/authentication.md`](../sdk/workbuddy-enterprises/python-sdk/docs/authentication.md)

## 核心约束

企业管理 OpenAPI **只接受企业应用身份**：

- OAuth2 `client_credentials`（admin 开发平台创建的应用）
- 或应用详情里创建的 `pt_` 开头 API Key

个人 API Key 调管理类接口通常会 **403**。

## 环境变量

| 变量 | 必填 | 说明 |
|---|---|---|
| `WORKBUDDY_ENTERPRISE_ID` | 是 | 企业 ID，默认显式配置 |
| `WORKBUDDY_CLIENT_ID` | 与 secret 成对 | OAuth client id |
| `WORKBUDDY_CLIENT_SECRET` | 与 id 成对 | OAuth client secret |
| `WORKBUDDY_API_KEY` | 二选一 | 应用级 API Key |
| `WORKBUDDY_BASE_URL` | 否 | 默认 `https://api.copilot.tencent.com/api/v1` |
| `WORKBUDDY_TOKEN_URL` | 否 | 默认 `https://copilot.tencent.com/oauth2/token` |

规则：

1. `client_id` 与 `client_secret` 必须成对提供；任一 OAuth 残项（包括已设置但为空）与 API Key 同时存在也会被拒绝
2. **OAuth 与 API Key 不能同时提供**
3. `enterprise_id` 不靠“猜”；JWT 解析 `ent-member:{id}` 只是辅助，不是默认配置路径
4. 专享版/私有化请改 `BASE_URL` / `TOKEN_URL`

## 调用头

```text
Authorization: Bearer <access_token_or_api_key>
Accept: application/json
```

## 错误分层（两端一致思想）

| 类型 | 含义 |
|---|---|
| 配置错误 | 缺 enterprise_id、双凭据并存等 |
| 鉴权错误 | token 获取失败 |
| HTTP 错误 | 非 2xx |
| API 错误 | HTTP 2xx 但业务 `code != 0` |

异常/错误对象应尽量保留 `request_id`，且**不要**把 secret 打进日志。

## 安全

- 不把真实密钥写入仓库、测试快照、截图、PR 正文  
- `local/`、`.env` 已在 ignore 策略中  
- live 写操作（delete/revoke/quota/upload）默认应额外确认  
