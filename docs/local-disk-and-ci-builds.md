# 本机磁盘压力与 CI 构建策略

> 状态：已记录的工程约束（需求备忘）  
> 适用范围：本仓库全部 SDK / CLI（当前 Python，以及未来可能的 Rust 等）  
> 创建目的：**减少本机磁盘压力**，避免构建缓存、虚拟环境、依赖目录污染工作区与 Git 历史

## 1. 需求摘要

本仓库在本机主要用于**阅读、小改、联调证据**；**不应**成为重型编译/依赖缓存场。

明确要求：

1. **优先远程 CI 产出构建与测试结果**，而不是在本机反复 `build` / 装全家桶依赖。
2. **构建产物、缓存、虚拟环境不得提交**进 Git。
3. **Rust SDK / CLI（已落地路径 `sdk/workbuddy-enterprises/rust-sdk`）默认采用 CI-only build** 策略：本机可不安装 Rust 工具链，也不保留项目级 `target/`。
4. `local/` 仅存放本机快照（如 OpenAPI yaml），已 gitignore，不作为发布内容。

一句话：

> **源码进仓库；胖东西进 CI 或本机可删缓存；Git 永远保持轻。**

## 2. 为什么要单独写这条

| 风险 | 说明 |
|---|---|
| Python `.venv` | 可达数十 MB 级；不应提交 |
| Rust `target/` | 很容易到数百 MB～数 GB；最危险 |
| Cargo / rustup 全局缓存 | 装在用户目录，不进仓库，但会占本机盘 |
| Node `node_modules` | 若未来出现，同属高风险，默认不引入 |
| 误提交二进制 / wheel / zip | 导致 Git 历史永久变胖 |

本机磁盘与 Git 历史是两类成本：本策略两者都要压。

## 3. 默认工作模式

### 3.1 Python（已有 `sdk/workbuddy-enterprises/python-sdk`）

**允许：**

- 轻量 editable install：`pip install -e ".[dev]"`（若本机已有 Python）
- 跑单元/合同测试：`pytest tests/unit tests/contract`
- 只读 live smoke（显式凭据、不写企业资源）

**避免：**

- 在仓库内长期保留多个 `.venv`
- 提交 `dist/`、`build/`、`*.egg-info/`、`.pytest_cache/`
- 把 skill zip、密钥、完整巨型规范快照当常规提交物

**更推荐：**

- PR / push 后看 GitHub Actions 的 test + wheel 产物
- 需要分发时从 CI artifact 取，而不是本机反复 `python -m build` 堆 `dist/`

### 3.2 Rust（已落地，强制 CI-only）

**默认：完全依赖 CI 构建，不依赖本机 Rust 缓存。**

> **硬约束（当前 goal）：开发 Rust SDK/CLI 时，不要在本机部署/启用 Rust 构建流程。**  
> 即使机器上碰巧已有 `rustc`/`cargo`，也**不要**在本仓库对 `rust-sdk` 执行 `cargo build` / `cargo test` / `cargo run`。  
> 验证与产物只认 GitHub Actions。

| 项 | 策略 |
|---|---|
| 本机是否必须安装 `rustup` / `cargo` | **否** |
| 项目目录是否保留 `target/` | **否（gitignore，且默认不本地编译）** |
| 测试 / release 二进制 | **GitHub Actions 产出 artifact** |
| 开发反馈环 | 改源码 → push/PR → 看 CI 日志；需要时下载 artifact |
| 仓库路径 | `sdk/workbuddy-enterprises/rust-sdk/`（与 `python-sdk/` 平行） |
| CI workflow | `.github/workflows/rust-sdk.yml` |

**允许例外（需自觉清理）：**

- 临时本机 `cargo test` / `cargo build` 排查 CI 难复现问题  
- 用完执行 `cargo clean`，确认 `target/` 未 staged

**禁止：**

- 提交 `target/`
- 把 release 二进制当源码仓常驻文件
- 为“方便”在文档里引导每人先本地编译一整套工具链（除非单独的高级附录）

### 3.3 CI 侧（可有缓存，但不落你的笔记本仓库）

CI 可以使用 Actions cache 加速依赖下载：

- 缓存位于 GitHub runner / 缓存服务
- **不**等于本机 `target/` 或仓库变胖
- 这是推荐做法

## 4. Git / 目录硬约束

必须忽略（已在根 `.gitignore` 覆盖或应保持覆盖）：

```text
local/
.env
.venv/
dist/
build/
**/dist/
**/build/
**/*.egg-info/
target/          # Rust（预留）
**/target/
.pytest_cache/
__pycache__/
```

`local/` 用途：

- 本机 OpenAPI 快照等
- **不提交**
- README 只记录 URL / 抓取时间 / SHA-256，不把整份规范当默认 Git 内容

## 5. 文档与实现的先后顺序（本条相关）

与“减少本机磁盘压力”相关的演进顺序：

1. ~~先写清约束~~（本文档）  
2. ~~落地 `rust-sdk` 源码 + CI workflow~~  
3. 默认不在 README 主路径教本机构建 Rust  
4. Python 继续作为可嵌入主 SDK；Rust 优先是 **CI 产出的 CLI 二进制**（`workbuddy` artifact）

## 6. 验收标准（本需求是否被遵守）

| 检查项 | 通过标准 |
|---|---|
| `git status` | 无 `.venv` / `target` / `dist` / 密钥 / skill zip |
| 仓库体积 | 以源码与文档为主，无大型二进制历史 |
| CI | Python（及未来 Rust）测试/构建在 Actions 可完成 |
| 本机可选 | 不装 Rust 也能贡献源码（靠 CI 验证） |
| 文档 | 根 README 能链到本文，贡献者看得到 |

## 7. 非目标

本文**不**要求：

- 立刻实现 Rust SDK / CLI  
- 禁止本机安装 Python  
- 禁止 CI 使用 cache  
- 把所有验证都搬到云端（只读 live 仍可在本机受控执行）

## 8. 相关路径

| 路径 | 说明 |
|---|---|
| [`../README.md`](../README.md) | 仓库入口 |
| [`../sdk/workbuddy-enterprises/python-sdk/`](../sdk/workbuddy-enterprises/python-sdk/) | 当前 Python SDK |
| [`../.github/workflows/ci.yml`](../.github/workflows/ci.yml) | 当前 CI |
| [`../.gitignore`](../.gitignore) | 忽略规则 |
| [`sdk/workbuddy-enterprises/rust-sdk/`](../sdk/workbuddy-enterprises/rust-sdk/) | Rust SDK + CLI 源码（**CI-only build**） |
| [`.github/workflows/rust-sdk.yml`](../.github/workflows/rust-sdk.yml) | Rust fmt/clippy/test/release + artifact |

## 9. 变更记录

| 日期 | 说明 |
|---|---|
| 2026-07-27 | 首次记录：减少本机磁盘压力；Rust 若落地则默认 CI-only build |
| 2026-07-27 | Rust SDK/CLI 源码与 CI workflow 落地；重申禁止本机构建 |
