# CI-only build (mandatory)

This crate must **not** be built on developer laptops as part of normal workflow.

## Allowed

- Edit `.rs` / `Cargo.toml` / docs
- Push PR / workflow_dispatch
- Download `workbuddy` artifact from GitHub Actions

## Forbidden (routine)

```bash
cargo build
cargo test
cargo run
cargo clippy
```

Even if `rustc`/`cargo` already exist on the machine, do not use them for this package unless debugging a CI-only failure, and then run `cargo clean` afterwards.

Policy source: `docs/local-disk-and-ci-builds.md`
