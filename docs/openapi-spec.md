# OpenAPI 规范来源（api.yaml）

## 官方地址（权威来源）

| 类型 | URL |
|---|---|
| **OpenAPI 规范文件 `api.yaml`** | https://www.codebuddy.cn/apiDocs/api.yaml |
| 文档站（人读 UI） | https://www.codebuddy.cn/apiDocs/index.html |
| 开放平台手册 | https://www.codebuddy.cn/apiDocs/open-platform.html |

说明：

1. **机器可读契约以 `api.yaml` 为准**，不是以文档站 HTML 文案为准。
2. 文档站是 Stoplight 风格前端，页面展示内容来自上述规范（及站点配置）。
3. 本仓库 SDK **手写**客户端；`api.yaml` 用于对照字段、路径、覆盖检查，**不是**用 OpenAPI Generator 生成公开 API 的主路径。

## 服务地址（写在规范里）

规范中的 server 形态：

```text
{serviceHost}/api/v1
```

| 变量 | 默认值 |
|---|---|
| serviceHost | https://api.copilot.tencent.com |
| 完整默认 base | https://api.copilot.tencent.com/api/v1 |

专享版/私有化使用组织自己的主域名，通过环境变量覆盖：

```text
WORKBUDDY_BASE_URL=https://<your-host>/api/v1
WORKBUDDY_TOKEN_URL=https://<your-token-host>/oauth2/token
```

OAuth token 默认（中国区常用）：

```text
https://copilot.tencent.com/oauth2/token
```

## 本机快照（可选，不进 Git）

为了离线对照与 inventory，可以把规范下载到仓库根：

```bash
mkdir -p local
curl -fsSL -o local/codebuddy-openapi-api.yaml \
  https://www.codebuddy.cn/apiDocs/api.yaml
```

| 项 | 约定 |
|---|---|
| 本地路径 | `local/codebuddy-openapi-api.yaml` |
| 是否提交 | **否**（`local/` 已 gitignore） |
| 用途 | 离线阅读、`tools/inventory_openapi.py` 覆盖盘点 |
| 文档应记录 | 官方 URL + 抓取时间 + 文件 SHA-256 + paths/ops 数量 |

### 实现期使用过的快照元数据（2026-07-27，2026-07-28 再核对）

> 仅作历史锚定；上游更新后以线上 `api.yaml` 为准，并应重算 hash。

| 字段 | 值 |
|---|---|
| Source URL | https://www.codebuddy.cn/apiDocs/api.yaml |
| Captured | 2026-07-27（Asia/Shanghai） |
| Re-verified | 2026-07-28（线上与本地逐字节一致） |
| Local path | `local/codebuddy-openapi-api.yaml`（不提交） |
| Size | 238,561 bytes / 5,597 lines |
| SHA-256 | `e6c6e6f8c350a4219a45f1b6d488d4b38d29c3e2a872d4b1b31c46774b0638fe` |
| Paths / operations（当时解析） | 66 / 73 |

校验示例：

```bash
shasum -a 256 local/codebuddy-openapi-api.yaml
```

盘点示例（Python 包工具）：

```bash
cd sdk/workbuddy-enterprises/python-sdk
python tools/inventory_openapi.py ../../../local/codebuddy-openapi-api.yaml
```

## 契约测试使用方式

Python contract tests 按以下顺序定位规范：

1. 环境变量 `WORKBUDDY_OPENAPI_SPEC` 指向的文件
2. 仓库根 `local/codebuddy-openapi-api.yaml`

未找到规范时，基础 mock method/path/body smoke 仍会运行，YAML 专项断言会明确标记为
skip；CI 始终提供官方规范，因此不会以降级模式通过门禁。

GitHub Actions 会在 runner 临时目录下载上述官方 URL，并通过
`WORKBUDDY_OPENAPI_SPEC` 交给测试；规范不会因此写入 Git 或发布产物。

当前自动化校验覆盖：

- 官方 YAML 的 73-operation exact set、HTTP method/path 与 path 参数；
- 全部 query 字段及 required query；
- JSON/multipart request media type、全部顶层 body properties 与 required fields；
- Python mock 的 primitive wire type、enum、嵌套 required/声明字段、multipart package 与
  无 request body 的 POST；
- Rust `OperationSpec` registry 的 method/path、path/query、body kind、allowed/required body
  metadata；Rust manifest/helper tests 另行检查 registry 自洽、write 分类、required query、
  path rendering 与三类 body transport metadata。

它不是完整的 OpenAPI Schema validator：仍不覆盖所有 `format`、`minimum` / `maximum`、
`minItems` / `maxItems`、跨字段业务条件或完整 response schema，也不替代真实企业 live 验证。

## 规范与本仓库 SDK 的关系

```text
https://www.codebuddy.cn/apiDocs/api.yaml   <- 权威契约
                 |
                 v
        对照 / inventory / 覆盖矩阵
                 |
                 v
   python-sdk / rust-sdk（手写客户端）
```

- **来源**：腾讯云代码助手 / CodeBuddy 公开 API 文档站点
- **本仓库不重新发布整份 `api.yaml` 进 Git**（除非另行确认再分发许可）
- 覆盖情况见：[`../sdk/workbuddy-enterprises/python-sdk/docs/api-coverage.md`](../sdk/workbuddy-enterprises/python-sdk/docs/api-coverage.md)

## 相关文档

- [overview.md](overview.md)
- [getting-started.md](getting-started.md)
- [architecture.md](architecture.md)
- [local-disk-and-ci-builds.md](local-disk-and-ci-builds.md)
