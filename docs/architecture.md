# 架构与目录分层

## 设计原则

1. **仓库是多语言工作区**，不是单文件脚本堆  
2. **按产品域再按语言** 分层，避免根目录直接塞实现  
3. **SDK 与产品服务分离**：本仓只放客户端；自动上下架策略以后另做  
4. **Python 可本机轻测；Rust 默认 CI 构建**，控制本机磁盘  

## 目录树

```text
tencent-workbuddy-sdk/
  README.md
  LICENSE
  docs/                              # 仓库级文档（你现在在这里）
  .github/workflows/
    ci.yml                           # Python 测试 + wheel
    rust-sdk.yml                     # Rust fmt/clippy/test/release + CLI artifact
  local/                             # 本机 OpenAPI 快照等（gitignore）
  sdk/
    README.md
    workbuddy-enterprises/           # 企业 OpenAPI 客户端族
      README.md
      python-sdk/                    # Python 实现
        pyproject.toml
        src/workbuddy_enterprise/
        tests/
        docs/
        examples/
      rust-sdk/                      # Rust 实现 + CLI
        Cargo.toml
        src/lib.rs
        src/bin/workbuddy.rs
        CI_ONLY_BUILD.md
```

命名说明：

| 名字 | 含义 |
|---|---|
| `sdk/` | 所有客户端 SDK 根 |
| `workbuddy-enterprises/` | 企业 OpenAPI 领域（可平行加其他领域） |
| `python-sdk` / `rust-sdk` | 语言实现目录 |
| 包名 `workbuddy-enterprise` | distribution / crate 名（单数 enterprise） |

## 运行时分层（目标产品视角）

```text
未来：Skill 治理产品
  inventory / plan / approval / apply / audit
                 │
                 ▼
     workbuddy_enterprise SDK（Python 或 Rust）
                 │
                 ▼
     CodeBuddy Enterprise OpenAPI
```

当前仓库只负责中间 SDK 层（Rust 额外带 CLI）。

## 双语言职责建议

| 语言 | 更适合 |
|---|---|
| Python | 业务服务嵌入、批处理、数据/自动化脚本、快速迭代 |
| Rust | 单文件 CLI 分发、无 Python 环境的机器、后续若要更强分发控制 |

两套客户端应尽量保持**资源命名与鉴权语义一致**，但不强制 API 逐符号镜像。

## 模块划分（两边共通）

- `auth`：OAuth client_credentials / API Key  
- `client`：统一 HTTP、错误、requestId  
- `resources/*`：enterprise / users / members / licenses / usage / groups / models / skills / categories / experts / analytics  
- Python 另有 `schemas` 与 contract tests  
- Rust 另有 `bin/workbuddy` CLI  

## 非目标架构

- 不把 OpenAPI Generator 生成物当公开主 API  
- 不在本仓做 monorepo 应用服务  
- 不把 `local/`、密钥、构建缓存纳入版本真相  
