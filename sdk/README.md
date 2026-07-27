# SDK tree

```text
sdk/
  workbuddy-enterprises/
    python-sdk/     # Python package: workbuddy-enterprise
    rust-sdk/       # Rust crate + workbuddy CLI (CI-only build)
```

## Disk / CI policy

See:

[`docs/local-disk-and-ci-builds.md`](../docs/local-disk-and-ci-builds.md)

Rust builds are performed **only** in GitHub Actions. Do not create local `target/` for routine development.
