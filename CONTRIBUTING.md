# Contributing to AI-Based Interview Preparation Assistant

Thank you for contributing to this MLOps project! This repository follows production-grade MLOps engineering standards combined with academic rigor.

---

## 1. Development Environment Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Tejzraj/MLOps.git
   cd MLOps
   ```

2. **Initialize a virtual environment:**
   ```bash
   make setup-env
   source .venv/bin/activate
   ```

3. **Install development dependencies:**
   ```bash
   make install-dev
   ```

---

## 2. Git Workflow & Branching

- Work on feature branches branched from `main`:
  ```bash
  git checkout -b feature/phase1-eda
  # or
  git checkout -b fix/params-config
  ```
- Use conventional commit messages:
  - `feat:` New features or pipeline additions
  - `fix:` Bug fixes
  - `docs:` Documentation improvements
  - `chore:` Configuration, dependencies, or maintenance
  - `refactor:` Code refactoring without behavior modification

---

## 3. Code Quality Standards

Before committing, run code formatting and linting:
```bash
make format
make lint
make test
```

- **Formatting:** Python code is formatted with `black` (100 character line length).
- **Linting:** Clean checks with `ruff`.
- **Typing & Docstrings:** All public functions should include type hints and clear docstrings.

---

## 4. MLOps Data & Artifact Rules

> [!CAUTION]
> **Strict Repository Invariants:**
> 1. **Never commit raw or processed datasets to Git:** Always track datasets via DVC (`dvc add data/raw/...`).
> 2. **Never commit model binary files (`.pkl`, `.joblib`, `.onnx`):** Version models using DVC or the MLflow Model Registry.
> 3. **Never commit secrets or credentials:** Keep credentials in environment variables or `.env` (which is gitignored).

---

## 5. Submitting Pull Requests

1. Ensure your branch is rebased on latest `main`.
2. Verify all tests pass locally.
3. Fill out the PR template thoroughly.
4. Request a review from the repository maintainer.
