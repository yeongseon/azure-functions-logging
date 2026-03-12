VENV_DIR := .venv
PIP := $(VENV_DIR)/bin/pip
HATCH := $(VENV_DIR)/bin/hatch
BOOTSTRAP_PYTHON := $(shell command -v python3.10 || command -v python3)
PACKAGE_INIT := $(shell find src -mindepth 2 -maxdepth 2 -name "__init__.py" | head -n1)

.PHONY: bootstrap
bootstrap:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Creating virtual environment..."; \
		$(BOOTSTRAP_PYTHON) -m venv $(VENV_DIR); \
	fi
	@echo "Ensuring Hatch is installed in virtual environment..."
	@$(PIP) install --upgrade pip > /dev/null
	@$(PIP) install hatch > /dev/null
	@echo "Hatch installed at $(HATCH)"

.PHONY: ensure-hatch
ensure-hatch: bootstrap

.PHONY: install
install: ensure-hatch
	@$(HATCH) env create
	@if [ -n "$$CI" ]; then \
		echo "CI detected: skipping pre-commit hook installation"; \
	else \
		$(MAKE) precommit-install 2>/dev/null || true; \
	fi

.PHONY: format
format: ensure-hatch
	@$(HATCH) run format

.PHONY: style
style: ensure-hatch
	@$(HATCH) run style

.PHONY: typecheck
typecheck: ensure-hatch
	@$(HATCH) run typecheck

.PHONY: lint
lint: ensure-hatch
	@$(HATCH) run lint

.PHONY: security
security: ensure-hatch
	@$(HATCH) run security

.PHONY: check
check: ensure-hatch
	@$(MAKE) lint
	@$(MAKE) typecheck
	@echo "Lint and type check passed."

.PHONY: check-all
check-all: ensure-hatch
	@$(MAKE) check
	@$(MAKE) test
	@$(MAKE) security
	@echo "All checks passed including tests and security scan."

.PHONY: precommit-install
precommit-install:
	@pre-commit install 2>/dev/null || echo "pre-commit not installed; skipping hook setup"

.PHONY: test
test: ensure-hatch
	@echo "Running tests..."
	@$(HATCH) run test

.PHONY: cov
cov: ensure-hatch
	@$(HATCH) run cov
	@echo "coverage.xml generated for Codecov upload."

.PHONY: build
build: ensure-hatch
	@$(HATCH) build

.PHONY: clean
clean:
	@rm -rf *.egg-info dist build __pycache__ .pytest_cache

.PHONY: clean-all
clean-all: clean
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete
	@rm -rf .mypy_cache .ruff_cache .pytest_cache .coverage coverage.xml htmlcov .DS_Store $(VENV_DIR)

.PHONY: help
help:
	@echo "Available commands:" && \
	grep -E '^\.PHONY: ' Makefile | cut -d ':' -f2 | xargs -n1 echo "  - make"
