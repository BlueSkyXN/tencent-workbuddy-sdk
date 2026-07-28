# CI 与产物

## Workflows

| 文件 | 名称 | 作用 |
|---|---|---|
| `.github/workflows/ci.yml` | `ci` | Python：pytest + build wheel/sdist，上传 `dist` artifact |
| `.github/workflows/rust-sdk.yml` | `rust-sdk` | Rust：fmt / clippy / test / release，上传 `workbuddy` CLI artifact |

触发：

- `push` / `pull_request`（`rust-sdk.yml` 带 path filter；`ci.yml` 当前为全量触发）  
- `workflow_dispatch` 可手动跑  

## Python 产物

成功 run 中 artifact 名通常为 **`dist`**，内含：

- `workbuddy_enterprise-*.whl`
- `workbuddy_enterprise-*.tar.gz`

本地常规开发优先：

```bash
cd sdk/workbuddy-enterprises/python-sdk
python -m pip install -e ".[dev]"
```

## Rust 产物

成功 run 中 artifact 名：**`workbuddy-cli-linux-x64`**

内含 release 二进制 `workbuddy`（当前 CI 跑在 `ubuntu-latest`）。

下载方式：

1. GitHub → Actions → `rust-sdk`  
2. 打开最新 **success** run  
3. Artifacts 区下载  

或用 `gh`：

```bash
gh run download <run-id> --repo BlueSkyXN/tencent-workbuddy-sdk -n workbuddy-cli-linux-x64
```

## 为什么 Rust 不在本机构建

见 [local-disk-and-ci-builds.md](local-disk-and-ci-builds.md)。

摘要：

- 避免 `target/` 占满本机盘  
- 统一工具链版本（当前 pin 见 `rust-sdk/rust-toolchain.toml`）  
- 源码提交后以 CI 结果为准  

## 绿不等于线上验收完成

| CI 绿 | 含义 |
|---|---|
| Python contract/unit 绿 | mock 合同与基础单元通过 |
| Rust fmt/clippy/test/release 绿 | 代码可编译、基础测试过、CLI 可打包 |
| 不自动证明 | 全部 73 个 operation 已在真实企业环境 live 验证（含写接口） |

live 只读/写操作仍需显式凭据与授权。
