# ==============================================================================
# Makefile: Developer Automation for MLOps Pipeline
# ==============================================================================

.PHONY: help setup-env install install-dev lint format test clean dvc-status mlflow-ui

PYTHON := python3
VENV := .venv
BIN := $(VENV)/bin

help:  ## Show this help message
	@echo "AI-Based Interview Preparation Assistant - Developer Automation"
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

setup-env:  ## Create virtual environment
	$(PYTHON) -m venv $(VENV)
	@echo "Virtual environment created at $(VENV). Activate with: source $(VENV)/bin/activate"

install:  ## Install core production dependencies
	pip install --upgrade pip
	pip install -r requirements.txt

install-dev:  ## Install development and testing dependencies
	pip install --upgrade pip
	pip install -r requirements-dev.txt
	pre-commit install || true

lint:  ## Run code linters (ruff, black check)
	ruff check src/ tests/ configs/
	black --check src/ tests/

format:  ## Auto-format codebase using black and ruff
	black src/ tests/
	ruff check --fix src/ tests/

test:  ## Run test suite with coverage
	pytest -v --cov=src --cov-report=term-missing tests/

clean:  ## Clean temporary caches, bytecode, and logs
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete

dvc-status:  ## Check DVC pipeline status
	dvc status

mlflow-ui:  ## Launch MLflow tracking server locally
	mlflow ui --port 5000
