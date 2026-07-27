# tencent-workbuddy-sdk

**Unofficial** multi-language client workspace for CodeBuddy / WorkBuddy integrations.

> Not an official Tencent package.

## Layout

```text
tencent-workbuddy-sdk/
  LICENSE
  README.md
  docs/
    local-disk-and-ci-builds.md   # 本机磁盘压力 / CI 构建约束
  sdk/
    workbuddy-enterprises/
      python-sdk/                 # Python Enterprise OpenAPI SDK
      rust-sdk/                   # Rust SDK + workbuddy CLI（CI-only build）
  local/                          # 本机快照（gitignored）
```

## Current SDKs

### Python

[`sdk/workbuddy-enterprises/python-sdk`](sdk/workbuddy-enterprises/python-sdk)

```bash
cd sdk/workbuddy-enterprises/python-sdk
python -m pip install -e ".[dev]"
python -m pytest tests/unit tests/contract
```

### Rust SDK + CLI

[`sdk/workbuddy-enterprises/rust-sdk`](sdk/workbuddy-enterprises/rust-sdk)

- Library: `workbuddy_enterprise`
- CLI binary: `workbuddy`
- **Build only in GitHub Actions** (see workflow `rust-sdk.yml`)
- **Do not** run `cargo build` / `cargo test` locally for this package

Download the CLI from Actions artifacts after CI succeeds.

## Engineering constraint: keep the laptop light

- Prefer GitHub Actions for heavy builds
- Never commit `.venv` / `dist` / `target` / secrets
- Rust is **CI-only** by policy

Full note: [`docs/local-disk-and-ci-builds.md`](docs/local-disk-and-ci-builds.md)
