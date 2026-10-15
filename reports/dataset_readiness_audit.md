# Phase 1 Dataset Readiness & Source Evaluation Audit

> **Project:** AI-Based Interview Preparation Assistant  
> **Course:** AI252TA – Machine Learning Operations | Semester V  
> **Date:** 2026-10-15  
> **Status:** AUDIT COMPLETE — Candidate Source Categorized as Question-Bank Only  
> **Auditor:** Senior MLOps Engineer & Project Mentor  

---

## 1. Executive Summary

This audit assesses the readiness of candidate datasets for Phase 1 of the **AI-Based Interview Preparation Assistant**. Specifically, we evaluated whether the community repository [`Krishnagangwal/CS-Fundamentals`](https://github.com/Krishnagangwal/CS-Fundamentals) can serve as the primary dataset for training our four-class candidate answer quality classifier (`Poor`, `Needs Improvement`, `Good`, `Excellent`).

### Core Findings
1. **Source Type Mismatch:** `Krishnagangwal/CS-Fundamentals` is a **study guide / question bank**, NOT a labeled machine learning dataset. It contains question prompts and reference textbook explanations, but **zero candidate responses and zero quality ratings**.
2. **Missing Ground Truth:** Supervised classification requires pairs of $(\text{Prompt}, \text{Candidate Answer}) \rightarrow \text{Quality Class}$. Ingesting questions alone provides only input prompt text, with no labels to train or evaluate a classifier.
3. **Severe Licensing Obstacles:** The repository has **no license** (`"license": null`). Under copyright law, all rights are reserved by the author. Furthermore, several files are third-party copyrighted materials (Dr. Mamta Bansal's OS textbook, Nicholas Zakas' book, Striver's SDE sheet solutions). It cannot be redistributed legally.
4. **Conclusion:** `CS-Fundamentals` can serve only as an informal reference for drafting question prompts. Full classifier training is **BLOCKED** until a genuinely labeled candidate-answer dataset is acquired or assembled under faculty approval.

---

## 2. Inventory of Audited Subject Material

| Domain / Subject | File Types Found | Question Prompts Available? | Graded Candidate Responses Available? | Suitable for Classifier Training? |
| :--- | :---: | :---: | :---: | :---: |
| **Operating Systems** | PDFs (scanned & textbook), Markdown README | Yes (~30 questions) | **NO (0 responses)** | **NO (Missing labels & responses)** |
| **Computer Networks** | Markdown notes, Roadmap, PDFs | Yes (~40 questions) | **NO (0 responses)** | **NO (Missing labels & responses)** |
| **DBMS & SQL** | Scanned handwritten notes, 8 PDFs | Yes (~80 questions) | **NO (0 responses)** | **NO (Missing labels & responses)** |
| **OOP (C++, Java, Python)** | 5 PDFs, Markdown README | Yes (~25 questions) | **NO (0 responses)** | **NO (Missing labels & responses)** |
| **Data Structures & Algorithms**| 4 PDFs, 2 DOCX | Yes (~50 questions) | **NO (0 responses)** | **NO (Missing labels & responses)** |
| **System Design & SE** | Markdown cheatsheet, 3 PDFs | Yes (~31 questions) | **NO (0 responses)** | **NO (Missing labels & responses)** |
| **HR & Behavioral** | 1 PDF, 1 Markdown prompt list | Yes (~25 prompts) | **NO (0 responses)** | **NO (Missing labels & responses)** |

---

## 3. Schema Gap Analysis (19-Field Pipeline Standard)

The repository's data pipeline enforces a strict 19-field schema (`src/data/validation.py`):

```text
[question_id, domain, difficulty, question_type, question, reference_answer,
 expected_concepts, candidate_answer, correctness_score, completeness_score,
 communication_score, total_score, quality_label, source, source_license,
 annotator_id, annotation_method, version, split_group]
```

### Field Availability Breakdown
* **Fields Directly Available from Source (2 / 19):**
  * `question`: Extracted from question lists and cheatsheets.
  * `source`: `Krishnagangwal/CS-Fundamentals`.
* **Fields Reliably Derivable / Curated (5 / 19):**
  * `question_id`: Systematically generated (e.g. `Q_CN_001`).
  * `domain`: Mapped to the 10 approved CS/AI domains.
  * `difficulty`: Assigned manually (`Easy`, `Medium`, `Hard`).
  * `question_type`: Classified manually (`Conceptual`, `Comparative`, `Diagnostic`, `Behavioral / HR`).
  * `split_group`: Pinned to `question_id` for anti-leakage grouping.
* **Fields Requiring Curriculum Review (2 / 19):**
  * `reference_answer`: Must be checked against approved academic curricula.
  * `expected_concepts`: Must be extracted as semicolon-delimited technical keywords.
* **Fields COMPLETELY ABSENT (10 / 19) — Requires Human Simulation & Rubric Labeling:**
  * `candidate_answer`: The candidate's response to be assessed.
  * `correctness_score`: Rubric rating ($0-5$).
  * `completeness_score`: Rubric rating ($0-5$).
  * `communication_score`: Rubric rating ($0-5$).
  * `total_score`: Arithmetic sum ($0-15$).
  * `quality_label`: Ordinal class ($0, 1, 2, 3$).
  * `annotator_id`: Anonymous reviewer key (`ANN_01`).
  * `annotation_method`: Human rubric scoring protocol.
  * `source_license`: Documented license (missing in source).
  * `version`: Dataset semantic versioning.

---

## 4. Academic Integrity & Scientific Rigor

A machine learning model trained on fabricated or arbitrarily assigned labels is scientifically invalid. In accordance with course guidelines for **AI252TA (MLOps - Semester V)**:
1. **No Synthetic Shortcuts:** We do not synthesize artificial student answers with self-assigned labels merely to make `dvc repro` pass.
2. **Strict Separation of Question Ingestion from Ground-Truth Labeling:** A question bank seeds the question database; ground-truth evaluation labels must come from human application of the standardized scoring rubric ([`docs/dataset/LABELING_GUIDELINES.md`](../docs/dataset/LABELING_GUIDELINES.md)).
3. **Transparent Reproduction Reporting:** Pipeline code is completely implemented, verified with 51 unit tests, and ready to ingest data. The honest status is **Pipeline Verified / Awaiting Approved Labeled Dataset**.

---

## 5. Recommended Action Plan

1. **Faculty Review:** Present [`docs/dataset/DATASET_APPROVAL.md`](../docs/dataset/DATASET_APPROVAL.md) and [`docs/dataset/CS_FUNDAMENTALS_SOURCE_AUDIT.md`](../docs/dataset/CS_FUNDAMENTALS_SOURCE_AUDIT.md) to your faculty guide.
2. **Question Bank Seeding (Pilot):** If approved, extract a small pilot of 12 questions from machine-readable Markdown files in `CS-Fundamentals` to seed the question bank.
3. **Candidate Response Generation & Labeling:** Follow the 10-stage protocol in [`docs/dataset/DATA_COLLECTION.md`](../docs/dataset/DATA_COLLECTION.md) to collect/draft candidate responses across all 4 tiers and perform human rubric labeling.
4. **Execute Pipeline:** Place the final labeled CSV at `data/raw/interview_data.csv` and execute `dvc repro`.
