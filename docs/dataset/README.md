# Dataset Documentation & Governance

> **Project:** AI-Based Interview Preparation Assistant<br>
> **Course:** AI252TA – Machine Learning Operations | Semester V<br>
> **Status:** Phase 1 — Dataset Specification & Approval In Progress

---

## 1. Directory Purpose

This directory serves as the centralized technical, legal, and pedagogical governance hub for all data used in the **AI-Based Interview Preparation Assistant**.

To ensure full academic defensibility and production-grade MLOps rigor, all dataset specifications, collection pipelines, scoring rubrics, and faculty review dossiers are maintained as version-controlled engineering documents.

---

## 2. Core Dataset Documentation Suite

| Document | Primary Focus | Status |
| :--- | :--- | :---: |
| **[`DATASET_SPECIFICATION.md`](DATASET_SPECIFICATION.md)** | End-to-end dataset specification: ML formulation, 19-field schema, 10 supported domains, 4 quality classes, group-based leakage prevention, and acceptance criteria. | `[~] PROPOSED` |
| **[`DATA_COLLECTION.md`](DATA_COLLECTION.md)** | Intended 10-stage collection, annotation, and validation pipeline from external question ingestion to human quality control and DVC versioning. | `[~] PLANNED` |
| **[`LABELING_GUIDELINES.md`](LABELING_GUIDELINES.md)** | Detailed annotation protocol across Correctness ($0-5$), Completeness ($0-5$), and Communication ($0-5$), with edge-case handling rules and human validation strategies. | `[~] PROPOSED` |
| **[`DATASET_APPROVAL.md`](DATASET_APPROVAL.md)** | Faculty-facing review dossier containing the academic defense, provenance justification, synthetic text bounds, and formal committee sign-off form. | `[ ] PENDING REVIEW` |

---

## 3. Current Dataset Status Notice

> **Important Notice:** No raw or synthetic datasets have been finalized or committed to Git. Dataset collection, human annotation, and DVC caching will commence immediately following committee sign-off on [`DATASET_APPROVAL.md`](DATASET_APPROVAL.md).
>
> For physical storage conventions, see [`data/README.md`](../../data/README.md).
