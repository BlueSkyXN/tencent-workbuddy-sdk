
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
- `cargo test`
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
let page = client.skills().list(SkillSource::Custom, None, None, Some(1), Some(20))?;
println!("total={:?}", page.total_count);
```

## CLI (after downloading CI artifact)

Environment:

```text
WORKBUDDY_ENTERPRISE_ID=...
WORKBUDDY_CLIENT_ID=...
WORKBUDDY_CLIENT_SECRET=...
# or WORKBUDDY_API_KEY=pt_...
```

Examples:

```bash
./workbuddy skills list --source custom
./workbuddy models list
./workbuddy enterprise info
./workbuddy members list --page-num 1 --page-size 20
```

Write commands exist but should be used carefully against real enterprises.

## Scope

Mirrors the Python SDK resource surface for Enterprise OpenAPI:

enterprise, users, members, licenses, usage, groups, models, skills,
skill_categories, experts, expert_categories, analytics.

## Local anti-patterns

```bash
# Do NOT do these for routine development in this repo:
cargo build
cargo test
cargo run
```

Exception only for rare CI-repro debugging; then `cargo clean` and ensure `target/` is untracked.
