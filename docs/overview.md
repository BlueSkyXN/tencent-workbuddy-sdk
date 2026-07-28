# 仓库概览

## 一句话

`tencent-workbuddy-sdk` 是**非官方**的 CodeBuddy / WorkBuddy **企业 OpenAPI** 客户端工作区，用于程序化调用企业管理接口（技能、模型、成员、额度等），不是腾讯官方 SDK，也不是 Agent 运行时 SDK。

## 解决什么问题

官方目前提供的是：

- 企业管理 OpenAPI 文档（`api.yaml`）
- Agent SDK / Cloud Agent SDK（另一套能力面）

**没有**覆盖 ` /enterprises/{enterpriseId}/openapi/... ` 这组企业管理接口的完整官方多语言客户端。

本仓库目标是提供可嵌入的客户端底座，支撑后续“Skill 生命周期治理 / 自动上下架”等产品，但**仓库本身先只做 SDK（和 Rust CLI）**，不做审批流、调度器、管理后台。

## 当前交付

| 组件 | 路径 | 形态 |
|---|---|---|
| Python SDK | `sdk/workbuddy-enterprises/python-sdk` | 库 `workbuddy_enterprise`，同步，`httpx` |
| Rust SDK | `sdk/workbuddy-enterprises/rust-sdk` | 库 `workbuddy_enterprise` |
| Rust CLI | 同上 crate 的 `workbuddy` binary | 从 GitHub Actions artifact 获取 |
| 工程约束文档 | `docs/` | 磁盘压力、CI-only、上手与架构 |

## 明确不在范围内

- 官方身份宣称 / 冒充腾讯发布
- Agent 对话运行时、Managed Agents / AgentOS 封装
- 自动上下架策略引擎、审批、审计库、Web UI
- 本机强制安装完整 Rust 工具链并长期保留 `target/`
- 把密钥、`.env`、`local/` 规范快照提交进 Git

## 与官方能力的边界

| 能力 | 官方主要入口 | 本仓库 |
|---|---|---|
| 企业 Skill / Model / Member 管理 OpenAPI | REST + `api.yaml` | **做** |
| 本地 Agent 执行 | `codebuddy-agent-sdk` / `@tencent-ai/agent-sdk` | **不做** |
| 云端 AgentOS | `codebuddy-cloud-agent-sdk` | **不做** |

## 契约来源

**权威 OpenAPI 文件：**

- `api.yaml`：https://www.codebuddy.cn/apiDocs/api.yaml  
- 文档站 UI：https://www.codebuddy.cn/apiDocs/index.html  
- 默认 API Base：`https://api.copilot.tencent.com/api/v1`  
- 默认 Token URL：`https://copilot.tencent.com/oauth2/token`  

完整说明（来源、下载、本机快照、SHA-256 锚定）：**[openapi-spec.md](openapi-spec.md)**

本机可把规范快照放到仓库根 `local/codebuddy-openapi-api.yaml`（已 gitignore），仅作离线对照，**不提交、不随仓库发布**。

## 许可证

仓库根 `LICENSE` 为 **GPL-3.0**。在嵌入其他产品前请自行评估许可证兼容性。
