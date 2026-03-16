# AGENTS.md

## Purpose
`azure-functions-logging` provides structured JSON logging for Azure Functions Python v2 applications.

## Read First
- `README.md`
- `CONTRIBUTING.md`
- `docs/agent-playbook.md`

## Working Rules
- The root logger is never modified by this library — only named loggers are configured.
- No runtime dependency on `azure-functions` — it is an optional import only.
- Runtime code must remain compatible with Python 3.10+.
- Public APIs must be fully typed.
- Keep documentation examples and tests synchronized with any behavior changes.

## Validation
- `make test`
- `make lint`
- `make typecheck`
- `make build`
