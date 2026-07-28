# 文档索引

本仓库文档分两层：

1. **仓库级文档**（本目录）：定位、上手、架构、鉴权总览、CI、本机磁盘策略  
2. **包级文档**：各语言 SDK 自己的 README 与更细的 API 说明  

## 仓库级

| 文档 | 说明 |
|---|---|
| [overview.md](overview.md) | 仓库是什么、不是什么、当前交付边界 |
| [getting-started.md](getting-started.md) | Python / Rust 最短上手路径 |
| [architecture.md](architecture.md) | 目录分层、双语言布局、职责边界 |
| [authentication.md](authentication.md) | 企业 OpenAPI 鉴权约定 |
| [ci-and-artifacts.md](ci-and-artifacts.md) | GitHub Actions 与产物获取 |
| [local-disk-and-ci-builds.md](local-disk-and-ci-builds.md) | 减少本机磁盘压力 / Rust CI-only |

## 包级

| 包 | 入口 |
|---|---|
| Python SDK | [`../sdk/workbuddy-enterprises/python-sdk/README.md`](../sdk/workbuddy-enterprises/python-sdk/README.md) |
| Python 鉴权细节 | [`../sdk/workbuddy-enterprises/python-sdk/docs/authentication.md`](../sdk/workbuddy-enterprises/python-sdk/docs/authentication.md) |
| Python 错误与分页 | [`../sdk/workbuddy-enterprises/python-sdk/docs/errors-and-pagination.md`](../sdk/workbuddy-enterprises/python-sdk/docs/errors-and-pagination.md) |
| Python API 覆盖矩阵 | [`../sdk/workbuddy-enterprises/python-sdk/docs/api-coverage.md`](../sdk/workbuddy-enterprises/python-sdk/docs/api-coverage.md) |
| Python live 测试 | [`../sdk/workbuddy-enterprises/python-sdk/docs/live-testing.md`](../sdk/workbuddy-enterprises/python-sdk/docs/live-testing.md) |
| Rust SDK + CLI | [`../sdk/workbuddy-enterprises/rust-sdk/README.md`](../sdk/workbuddy-enterprises/rust-sdk/README.md) |
| Rust CI-only 硬约束 | [`../sdk/workbuddy-enterprises/rust-sdk/CI_ONLY_BUILD.md`](../sdk/workbuddy-enterprises/rust-sdk/CI_ONLY_BUILD.md) |

## 阅读顺序建议

1. [overview.md](overview.md)  
2. [getting-started.md](getting-started.md)  
3. 按语言进入对应包 README  
4. 若会动 Rust 或担心本机膨胀：先看 [local-disk-and-ci-builds.md](local-disk-and-ci-builds.md)
