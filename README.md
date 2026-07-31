# tencent-workbuddy-sdk

**非官方** CodeBuddy / WorkBuddy **企业 OpenAPI** 多语言客户端工作区。

> Not an official Tencent package.  
> 覆盖当前官方 `api.yaml` 的 66 paths / 73 operations（skills / models / members / usage 等），
> **不是** Agent Runtime / AgentOS SDK。

## 文档入口

从这里开始：

**[docs/README.md](docs/README.md)**

常用：

| 文档 | 内容 |
|---|---|
| [docs/overview.md](docs/overview.md) | 仓库定位与边界 |
| [docs/openapi-spec.md](docs/openapi-spec.md) | **api.yaml 官方地址与来源** |
| [docs/getting-started.md](docs/getting-started.md) | Python / Rust 快速开始 |
| [docs/architecture.md](docs/architecture.md) | 目录分层与职责 |
| [docs/authentication.md](docs/authentication.md) | 鉴权约定 |
| [docs/ci-and-artifacts.md](docs/ci-and-artifacts.md) | CI 与产物下载 |
| [docs/local-disk-and-ci-builds.md](docs/local-disk-and-ci-builds.md) | 本机磁盘 / Rust CI-only |

## 目录结构

```text
tencent-workbuddy-sdk/
  docs/                         # 仓库级文档
  sdk/
    workbuddy-enterprises/
      python-sdk/               # Python SDK
      rust-sdk/                 # Rust SDK + workbuddy CLI（CI-only）
  local/                        # 本机快照（gitignore）
```

## 当前组件

### Python SDK

路径：[`sdk/workbuddy-enterprises/python-sdk`](sdk/workbuddy-enterprises/python-sdk)

```bash
cd sdk/workbuddy-enterprises/python-sdk
python -m pip install -e ".[dev]"
python -m pytest tests/unit tests/contract
```

### Rust SDK + CLI

路径：[`sdk/workbuddy-enterprises/rust-sdk`](sdk/workbuddy-enterprises/rust-sdk)

- 库名：`workbuddy_enterprise`
- CLI：`workbuddy`（从 Actions artifact `workbuddy-cli-linux-x64` 下载）
- 完整 CLI 入口：`workbuddy api <operation>`；用 `workbuddy operations` 查看 73 个 registry name
- **默认禁止本机 `cargo build/test/run`**，详见 [docs/local-disk-and-ci-builds.md](docs/local-disk-and-ci-builds.md)

## CI

| Workflow | 作用 |
|---|---|
| `ci` | 官方 YAML 对照、Python 测试、Ruff/Mypy 与 wheel |
| `rust-sdk` | Rust 检查、测试、release CLI artifact |

详情：[docs/ci-and-artifacts.md](docs/ci-and-artifacts.md)

## 许可证

GPL-3.0（见 [`LICENSE`](LICENSE)）。嵌入其他产品前请评估兼容性。
