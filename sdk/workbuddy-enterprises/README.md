# workbuddy-enterprises

非官方 CodeBuddy / WorkBuddy **企业 OpenAPI** 客户端集合。

Python SDK、Rust SDK library 和 Rust generic CLI 均映射当前官方 `api.yaml` 的全部
66 paths / 73 operations；这里的“全部”指 operation 与请求字段合同，不代表 73 个接口都已在
真实企业环境执行过 live 验证。

| 语言 | 路径 | 包 / 产物 | 本机构建预期 |
|---|---|---|---|
| Python | [python-sdk/](python-sdk/) | `workbuddy-enterprise` | 可轻量 editable install；打包优先 CI |
| Rust | [rust-sdk/](rust-sdk/) | lib + CLI `workbuddy` | **CI-only** |

仓库文档：

- [docs/overview.md](../../docs/overview.md)
- [docs/getting-started.md](../../docs/getting-started.md)
- [docs/architecture.md](../../docs/architecture.md)

不是腾讯官方包；不覆盖 Agent Runtime / AgentOS。
