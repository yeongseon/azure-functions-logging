VENV_DIR := .venv
PIP := $(VENV_DIR)/bin/pip
HATCH := $(VENV_DIR)/bin/hatch
BOOTSTRAP_PYTHON := $(shell command -v python3.10 || command -v python3)

.PHONY: bootstrap
bootstrap:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Creating virtual environment..."; \
		$(BOOTSTRAP_PYTHON) -m venv $(VENV_DIR); \
	fi
	@$(PIP) install --upgrade pip hatch > /dev/null

.PHONY: install
install: bootstrap
	@$(HATCH) env create

.PHONY: test
test: bootstrap
	@$(HATCH) run test

.PHONY: style
style: bootstrap
	@$(HATCH) run style

.PHONY: format
format: bootstrap
	@$(HATCH) run format

.PHONY: typecheck
typecheck: bootstrap
	@$(HATCH) run typecheck

.PHONY: clean
clean:
	@rm -rf .venv .hatch .pytest_cache .mypy_cache .ruff_cache build dist *.egg-info .coverage coverage.xml htmlcov
