# workbuddy-enterprise (Rust)

> 仓库总文档：[docs/README.md](../../../docs/README.md) · 快速开始：[docs/getting-started.md](../../../docs/getting-started.md) · CI-only：[CI_ONLY_BUILD.md](CI_ONLY_BUILD.md)

**Unofficial** synchronous Rust SDK + CLI for CodeBuddy / WorkBuddy **Enterprise OpenAPI**.

> Not an official Tencent package.  
> **Build policy: CI-only by default. Do not build or install a Rust toolchain for this crate on developer laptops.**

| Item | Value |
|---|---|
| Repo path | `sdk/workbuddy-enterprises/rust-sdk` |
| Library | `workbuddy_enterprise` |
| CLI binary | `workbuddy` |
| Python sibling | `../python-sdk` |

## OpenAPI source

权威规范：https://www.codebuddy.cn/apiDocs/api.yaml  
说明文档：[docs/openapi-spec.md](../../../docs/openapi-spec.md)

## Disk / build policy (hard rule)

This package is intentionally **CI-built**:

1. **Do not** run `cargo build` / `cargo test` / `cargo run` on local machines for routine work.
2. **Do not** keep project `target/` around; it is gitignored and treated as local pollution.
3. Install / test / release artifacts come from **GitHub Actions** only.
4. Full policy: [`docs/local-disk-and-ci-builds.md`](../../../docs/local-disk-and-ci-builds.md)

If you only edit source, push a PR and wait for CI.

## CI

Workflow: [`.github/workflows/rust-sdk.yml`](../../../.github/workflows/rust-sdk.yml)

CI will:

- `cargo fmt --check`
- `cargo clippy`
- `cargo test`（含仅绑定 `127.0.0.1` 的 typed/CLI HTTP contract tests）
- `cargo build --release`
- upload `workbuddy` release binary as an artifact

## Library quick shape

```rust
use workbuddy_enterprise::{Client, ClientConfig, SkillSource};

let client = Client::from_client_credentials(
    "client-id",
    "client-secret",
    "enterprise-id",
)?;
let page = client.skills().list(
    SkillSource::Custom,
    None,
    None,
    None,
    Some(1),
    Some(20),
)?;
println!("total={:?}", page.data.total_count);
```

## CLI (after downloading CI artifact)

Environment:

```text
WORKBUDDY_ENTERPRISE_ID=...
WORKBUDDY_CLIENT_ID=...
WORKBUDDY_CLIENT_SECRET=...
# or enterprise application API key created in the application details
# WORKBUDDY_API_KEY=pt_...
```

Personal API keys cannot call enterprise-management APIs. OAuth credentials must be a complete
`client_id` / `client_secret` pair and cannot be mixed with an application API key.

Examples:

```bash
./workbuddy skills list --source custom
./workbuddy models list
./workbuddy enterprise info
./workbuddy members list --page-num 1 --page-size 20

# 查看完整 73-operation registry
./workbuddy operations

# generic read operation：path/query 参数使用 YAML 原名
./workbuddy api models-available --query userId=u1

# JSON body 从文件或 stdin 读取；真实写操作还必须显式 --yes
./workbuddy api models-custom-create --body-file custom-model.json --yes

# multipart：普通字段可来自 JSON 文件，package 必须作为文件上传
./workbuddy api skills-create \
  --fields-file skill-fields.json \
  --package skill.zip \
  --yes
```

`--body-file -` 和 `--fields-file -` 可从 stdin 读取，避免把 `apiKey` 等敏感 JSON 放进
process argv。Registry 中标记为 mutation 的 generic operation 必须带 `--yes`；dashboard、
usage detail 等只读 POST 不要求 `--yes`。真实企业写操作仍应谨慎执行。

## Scope

Mirrors the Python SDK resource surface for Enterprise OpenAPI:

enterprise, users, members, licenses, usage, groups, models, skills,
skill_categories, experts, expert_categories, analytics.

The library and generic `workbuddy api <operation>` command cover all 73 operations in the current
OpenAPI contract. Legacy convenience subcommands remain a selected ergonomic subset; use
`workbuddy operations` to list registry names and `workbuddy api --help` for the generic flags.

[`src/operations.rs`](src/operations.rs) is the machine-readable CLI registry. CI compares its
method/path, path/query fields, request media kind, and top-level allowed/required body fields with
the downloaded official YAML. This is request-contract coverage, not full response-schema or live
enterprise verification.

## Local anti-patterns

```bash
# Do NOT do these for routine development in this repo:
cargo build
cargo test
cargo run
```

Exception only for rare CI-repro debugging; then `cargo clean` and ensure `target/` is untracked.
