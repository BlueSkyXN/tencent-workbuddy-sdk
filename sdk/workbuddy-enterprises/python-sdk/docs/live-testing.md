# Live testing

Live tests are opt-in and disabled by default.

## Read-only

```bash
export WORKBUDDY_LIVE=1
export WORKBUDDY_ENTERPRISE_ID=...
export WORKBUDDY_CLIENT_ID=...
export WORKBUDDY_CLIENT_SECRET=...
python -m pytest tests/live -m live
```

## Write tests

Not provided by default. Do not enable destructive live writes without explicit authorization and a disposable enterprise/test resource.
