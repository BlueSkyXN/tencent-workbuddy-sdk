# 本机磁盘压力与 CI 构建策略

> 状态：仓库长期工程约束  
> 目的：减少本机磁盘压力，避免构建缓存污染工作区与 Git 历史

## 1. 结论

| 对象 | 默认策略 |
|---|---|
| Python SDK | 允许轻量 `pip install -e` 与 pytest；打包优先 CI |
| Rust SDK / CLI | **CI-only build**；常规流程禁止本机 `cargo build/test/run` |
| Git | 不提交 `.venv` / `dist` / `target` / `.env` / `local/` 大快照 / 密钥 |

一句话：

> **源码进仓库；胖东西进 CI；本机保持轻。**

## 2. 为什么要约束

| 风险 | 说明 |
|---|---|
| Python `.venv` | 常见数十 MB，不应提交 |
| Rust `target/` | 动辄数百 MB～数 GB |
| Cargo/rustup 全局缓存 | 不在仓库内，但仍占本机盘 |
| 误提交 wheel/二进制/zip | Git 历史永久变胖 |

## 3. Python 工作方式

允许：

```bash
cd sdk/workbuddy-enterprises/python-sdk
python -m pip install -e ".[dev]"
python -m pytest tests/unit tests/contract
```

避免：

- 仓库内堆多个长期 `.venv`
- 提交 `dist/`、`build/`、`*.egg-info/`、`.pytest_cache/`
- 把密钥、skill zip、完整巨型规范当常规提交

更推荐：PR/push 后看 Actions 的 Python `dist` artifact。

## 4. Rust 工作方式（硬约束）

路径：`sdk/workbuddy-enterprises/rust-sdk/`  
Workflow：`.github/workflows/rust-sdk.yml`

### 常规允许

- 编辑 `.rs` / `Cargo.toml` / 文档  
- push / PR / `workflow_dispatch`  
- 从 Actions 下载 `workbuddy-cli-linux-x64`

### 常规禁止

```bash
cargo build
cargo test
cargo run
cargo clippy
```

即使本机已有 `rustc`/`cargo`，也不要对本 crate 做例行本地构建。

### 例外

仅当排查“CI 难复现”问题时可临时本地编译；结束后：

```bash
cargo clean
```

并确认 `target/` 未进入 git status。

## 5. Git ignore 关键项

至少覆盖：

```text
local/
.env
.venv/
dist/
build/
**/dist/
**/build/
**/*.egg-info/
target/
**/target/
.pytest_cache/
__pycache__/
```

`local/` 用途：本机 OpenAPI 快照等；README/docs 只记录 URL、抓取时间、SHA-256。

## 6. 验收清单

| 检查 | 通过标准 |
|---|---|
| `git status` | 无 venv/target/dist/密钥 |
| CI | Python / Rust workflow 可在 Actions 完成 |
| Rust 贡献 | 不装本机工具链也能改源码，靠 CI 验证 |
| 文档 | 根 README 能链到本文与 [README.md](README.md) 索引 |

## 7. 相关链接

| 路径 | 说明 |
|---|---|
| [getting-started.md](getting-started.md) | 上手 |
| [ci-and-artifacts.md](ci-and-artifacts.md) | 产物下载 |
| [`../sdk/workbuddy-enterprises/rust-sdk/CI_ONLY_BUILD.md`](../sdk/workbuddy-enterprises/rust-sdk/CI_ONLY_BUILD.md) | Rust 包内硬约束 |
| [`../.github/workflows/rust-sdk.yml`](../.github/workflows/rust-sdk.yml) | Rust CI |

## 8. 变更记录

| 日期 | 说明 |
|---|---|
| 2026-07-27 | 首次记录磁盘压力与 Rust CI-only 方向 |
| 2026-07-27 | Rust SDK/CLI 落地，重申禁止本机构建 |
| 2026-07-28 | 整理为正式仓库约束，并纳入 docs 索引体系 |
