# Project Status Dashboard

> **Project:** AI-Based Interview Preparation Assistant  
> **Course:** AI252TA – Machine Learning Operations  
> **Semester:** V  
> **Repository:** [https://github.com/Tejzraj/MLOps.git](https://github.com/Tejzraj/MLOps.git)  
> **Last Updated:** 2026-09-27  

---

## Current Status Overview

| Metric | Status |
| :--- | :--- |
| **Current Stage** | **PHASE 0 — FOUNDATION & REPRODUCIBILITY SETUP** |
| **Foundation Readiness** | `██████████` **100%** |
| **Phase 1 (Development & Reproducibility)** | `░░░░░░░░░░` **0% (In Preparation)** |
| **Phase 2 (Productionization & Deployment)** | `░░░░░░░░░░` **0% (Planned)** |
| **Phase 3 (Monitoring, Feedback & Governance)** | `░░░░░░░░░░` **0% (Planned)** |

---

## Milestone Breakdown

### Phase 0 — Foundation & Repository Architecture
- [x] Git repository configured with clean remote tracking
- [x] Standardized MLOps directory hierarchy initialized
- [x] Orange/Dark futuristic UI visual theme established
- [x] Configuration systems initialized (`params.yaml`, `configs/config.yaml`)
- [x] Dependency management defined (`requirements.txt`, `requirements-dev.txt`, `pyproject.toml`)
- [x] DVC pipeline blueprint initialized (`dvc.yaml`)
- [x] Developer workflows and linting automated (`Makefile`, `ruff`, `black`, `pytest`)
- [x] Comprehensive documentation framework created (`docs/`, `data/README.md`)
- [x] Open-source and academic governance added (`LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `CHANGELOG.md`)

### In Progress
- [~] Phase 1 preparation: dataset schema formalization and approval criteria
- [~] Preprocessing and feature engineering interface design

### Next Immediate Actions (Phase 1 Kickoff)
- [ ] Dataset sourcing and academic approval
- [ ] DVC remote and local cache initialization
- [ ] Exploratory Data Analysis (`notebooks/01_data_exploration.ipynb`)
- [ ] Data preprocessing and cleaning pipeline (`src/data/preprocess.py`)
- [ ] TF-IDF / feature extraction baseline (`src/features/build_features.py`)
- [ ] Baseline model training with MLflow tracking (`src/models/train_baseline.py`)
- [ ] Initial evaluation and metrics calculation (`src/evaluation/evaluate.py`)
