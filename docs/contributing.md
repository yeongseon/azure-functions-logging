# Contributing

Thank you for your interest in contributing to `azure-functions-logging`!

## How to Contribute

1. Fork the repository on GitHub.
2. Create a new branch for your feature or bug fix.
3. Make your changes and write tests.
4. Run all checks locally: `make check-all`.
5. Commit your changes using the Conventional Commits format.
6. Push your branch and open a pull request.

## Development Commands

Use the following `make` commands to automate common tasks:

| Command | Description |
|---------|-------------|
| `make format` | Format code with ruff and black |
| `make style` | Lint with ruff |
| `make typecheck` | Type check with mypy |
| `make lint` | Run both style and typecheck |
| `make test` | Run tests with pytest |
| `make cov` | Run tests and generate coverage report |
| `make security` | Run bandit security scan |
| `make check-all` | Run full local gate |

## Commit Message Format

We follow the Conventional Commits specification. This ensures a clean and searchable commit history.

| Type | Description |
|------|-------------|
| `feat` | A new feature |
| `fix` | A bug fix |
| `docs` | Documentation changes |
| `style` | Formatting, missing semi-colons, etc. |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `test` | Adding missing tests or correcting existing tests |
| `chore` | Changes to the build process or auxiliary tools |

### Commit Examples

* `feat: add JsonFormatter for structured logging`
* `fix: handle missing context object in inject_context`
* `docs: update troubleshooting guide`

## Version Management

Before creating a release, ensure you have:

1. Updated the version in `src/azure_functions_logging/__init__.py`.
2. Documented all changes in `CHANGELOG.md`.
3. Verified that `make check-all` passes with no errors.

## Pre-commit Hooks

Ensure pre-commit hooks are installed and active:

```bash
pre-commit install
```

## Code of Conduct

We are committed to fostering a welcoming and inclusive community. Please be respectful and inclusive in all interactions related to this project.
