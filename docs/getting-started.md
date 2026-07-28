# 快速开始

## 前置条件

1. 企业开放平台应用身份（**不是**个人 API Key 调管理接口）
2. 明确的 `enterprise_id`
3. 二选一凭据：
   - OAuth：`client_id` + `client_secret`
   - 或应用级 `pt_...` API Key

环境变量统一约定：

```text
WORKBUDDY_ENTERPRISE_ID=...
WORKBUDDY_CLIENT_ID=...
WORKBUDDY_CLIENT_SECRET=...
# 或者
WORKBUDDY_API_KEY=pt_...

# 可选（专享版/私有化）
WORKBUDDY_BASE_URL=https://api.copilot.tencent.com/api/v1
WORKBUDDY_TOKEN_URL=https://copilot.tencent.com/oauth2/token
```

> 同时提供 OAuth 与 API Key 会被 SDK 拒绝，避免隐式优先级。

---

## 路径 A：Python SDK（推荐嵌入业务）

```bash
cd sdk/workbuddy-enterprises/python-sdk
python -m pip install -e ".[dev]"
```

```python
from workbuddy_enterprise import WorkBuddyClient
from workbuddy_enterprise.types import SkillSource

with WorkBuddyClient.from_env() as client:
    resp = client.skills.list(source=SkillSource.CUSTOM, page_num=1, page_size=20)
    print(resp.request_id, resp.data.total_count)
    for skill in resp.data.items:
        print(skill.name, skill.version, skill.enabled)
```

更多：

- 包 README：[`../sdk/workbuddy-enterprises/python-sdk/README.md`](../sdk/workbuddy-enterprises/python-sdk/README.md)
- 示例：`sdk/workbuddy-enterprises/python-sdk/examples/`
- 测试：`python -m pytest tests/unit tests/contract`

---

## 路径 B：Rust CLI（推荐运维只读/脚本，CI 产物）

**不要本机 `cargo build`。** 从 GitHub Actions 下载 artifact。

1. 打开仓库 Actions → workflow **`rust-sdk`**
2. 选最新成功 run
3. 下载 `workbuddy-cli-linux-x64`
4. 解压得到 `workbuddy`，赋予执行权限

```bash
export WORKBUDDY_ENTERPRISE_ID=...
export WORKBUDDY_CLIENT_ID=...
export WORKBUDDY_CLIENT_SECRET=...

./workbuddy version
./workbuddy enterprise info
./workbuddy skills list --source custom
./workbuddy models list
./workbuddy members list --page-num 1 --page-size 20
```

写操作命令存在，但需要显式 `--yes`；对真实企业务必谨慎。

详情：[`../sdk/workbuddy-enterprises/rust-sdk/README.md`](../sdk/workbuddy-enterprises/rust-sdk/README.md)

---

## 路径 C：Rust 库（给其他 Rust 程序嵌入）

源码在 `sdk/workbuddy-enterprises/rust-sdk`。  
常规开发只改源码并走 CI；本机编译不是默认路径。

```rust
use workbuddy_enterprise::{Client, SkillSource};

let client = Client::from_env()?;
let page = client.skills().list(
    SkillSource::Custom,
    None,
    None,
    None,
    Some(1),
    Some(20),
)?;
```

---

## 常见第一坑

| 现象 | 常见原因 |
|---|---|
| 403 | 用了个人 API Key，或 enterprise 不匹配 |
| skills list 失败 | 漏了必填 `source=custom|builtin` |
| 想查“全部技能” | OpenAPI 无 all；需分别查 custom 与 builtin |
| Rust 本机编译很胖 | 违反 CI-only；见 [local-disk-and-ci-builds.md](local-disk-and-ci-builds.md) |
