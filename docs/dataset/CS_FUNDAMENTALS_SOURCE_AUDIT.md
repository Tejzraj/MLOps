# Source Audit: Krishnagangwal/CS-Fundamentals

> **Document Type:** External Dataset & Question-Bank Ingestion Audit  
> **Course:** AI252TA – Machine Learning Operations | Semester V  
> **Project:** AI-Based Interview Preparation Assistant  
> **Audited Repository:** [https://github.com/Krishnagangwal/CS-Fundamentals](https://github.com/Krishnagangwal/CS-Fundamentals)  
> **Audit Date:** 2026-10-15  
> **Auditor:** Senior MLOps Engineer & Project Mentor  

---

## 1. Executive Summary & Purpose

A candidate external source, [`Krishnagangwal/CS-Fundamentals`](https://github.com/Krishnagangwal/CS-Fundamentals), was evaluated to assess its suitability for ingestion into the **AI-Based Interview Preparation Assistant** pipeline.

### Core Verdict
1. **Suitable as a Question-Bank Inspiration Pool:** The repository contains lists of technical interview questions and study roadmaps across core computer science disciplines.
2. **UNSUITABLE for Direct Classifier Training:** The repository contains **ZERO candidate responses**, **ZERO dimensional scores**, and **ZERO quality classifications** ($0-3$). A question bank provides evaluation prompts, **not** labeled data for supervised machine learning.
3. **Severe Licensing & Attribution Obstacles:** The repository has **NO open-source license** (`"license": null`). Furthermore, multiple files are third-party copyrighted materials (such as a published textbook by Dr. Mamta Bansal, Striver's SDE sheet solutions, and Denny Zhang's cheatsheet). Direct redistribution in raw form presents copyright liabilities.

---

## 2. Repository Metadata & Structure

### Repository Overview
* **Repository:** `Krishnagangwal/CS-Fundamentals`
* **Default Branch:** `main` (commit `d8daa93...`)
* **Total Size:** ~284 MB (dominated by large scanned PDF files)
* **License:** `None` (no `LICENSE` file committed; GitHub API reports `"license": null`)

### File Format Distribution
| Format | Count | Characterization & Machine Readability |
| :--- | :---: | :--- |
| **Markdown (`.md`)** | **9** | **Fully machine-readable.** 4 top-level docs (`README.md`, `25-Job-Interview-Preparation-Prompts.md`, `List-of-Companies...`), 2 subject notes (`Computer-Network-Notes...`, `CN-Roadmap.md`, `System-Design-Cheatsheet.md`), and folder READMEs. |
| **Word Document (`.docx`)** | **3** | Binary Microsoft Word. Contains `Cover-Letter-Template.docx`, `Top-50-DSA-Interview-Questions.docx`, and `Learn-DSA-for-Free.docx`. Requires docx parsers; low metadata structure. |
| **PDF Document (`.pdf`)** | **23** | **Binary / Scanned PDFs.** Total volume > 270 MB. Includes handwritten scanned lecture notes (e.g., `Operating-System-Part-1.pdf` 43 MB, `Part-2.pdf` 39 MB, `DBMS-Handwritten-Notes.pdf` 13 MB, `DSA-Resource.pdf` 100 MB). OCR required; text parsing is brittle and error-prone. |

---

## 3. Subject-Wise Content & Provenance Analysis

### A. Operating Systems (`Operating-System/`)
* **Files Present:**
  * `Operating-System/Operating-System-Interview-Questions.pdf` (176 KB)
  * `Operating-System/Operating-System-Part-1.pdf` (43.2 MB) — Scanned handwritten notes.
  * `Operating-System/Operating-System-Part-2.pdf` (39.3 MB) — Scanned handwritten notes.
  * `Operating-System/Operating-System-Short-Notes.pdf` (8.1 MB)
  * `Operating-System/Operating-System-Textbook-Dr-Mamta-Bansal.pdf` (806 KB) — **Third-party published academic textbook**.
  * `Operating-System/README.md` (1.8 KB) — Topic outline list.
* **Audit Findings:** The textbook and scanned PDFs cannot be redistributed under open-source licenses. The interview questions PDF contains standard questions (Process vs. Thread, Virtual Memory, Deadlocks), but no graded candidate variations.

### B. Computer Networks (`Computer-Network/`)
* **Files Present:**
  * `Computer-Network/CN-Roadmap.md` (2.3 KB) — Markdown roadmap linking to GeeksforGeeks and YouTube.
  * `Computer-Network/Computer-Network-Notes-for-Placements-and-GATE.md` (8.9 KB) — **Clean, machine-readable Markdown notes** covering IP addressing, subnetting, NAT, and OSI layers.
  * `Computer-Network/Computer-Network-Notes-for-Placements-and-GATE.pdf` (7.0 MB)
  * `Computer-Network/Networking-Interview-Questions.pdf` (312 KB)
* **Audit Findings:** `Computer-Network-Notes-for-Placements-and-GATE.md` is the cleanest, most parseable text file in the entire repository, suitable for extracting reference concepts for networking questions.

### C. DBMS and SQL (`DBMS-and-SQL/`)
* **Files Present:**
  * `100-DBMS-Interview-Questions.pdf` (5.1 MB), `Complete-SQL-Cheatsheet.pdf` (30.1 MB), `DBMS-Handwritten-Notes.pdf` (13.2 MB), `DBMS-Notes.pdf` (843 KB), `LeetCode-SQL.pdf` (358 KB), `SQL-Interview-QA-2.pdf` (677 KB), `SQL-Interview-Questions-and-Answers.pdf` (2.2 MB), `SQL-Tutorial.pdf` (1.6 MB), `Top-50-SQL-Interview-Questions.pdf` (244 KB).
* **Audit Findings:** Significant redundancy across multiple overlapping SQL interview question PDFs. All files are binary PDFs. Zero machine-readable structured tabular data.

### D. Data Structures & Algorithms (`DSA/`)
* **Files Present:**
  * `Complete-Resources-of-DSA.pdf` (169 KB), `DSA-Cheatsheet.pdf` (99 KB), `DSA-Resource.pdf` (100.9 MB), `Learn-DSA-for-Free.docx` (9.9 KB), `Striver-SDE-Sheet-Solution.pdf` (17.6 MB), `Top-50-DSA-Interview-Questions.docx` (12.0 KB).
* **Audit Findings:** `Striver-SDE-Sheet-Solution.pdf` is proprietary content created by Raj Vikramaditya (takeUforward) and cannot be distributed.

### E. Object-Oriented Programming (`OOPs/`)
* **Files Present:**
  * `OOP-in-CPP.pdf` (165 KB), `OOPS-Concepts-in-Java.pdf` (1.0 MB), `OOPs-Interview-Questions.pdf` (435 KB), `Principles-of-OOP-JavaScript.pdf` (2.1 MB), `Python-OOP.pdf` (578 KB).
* **Audit Findings:** Covers C++, Java, Python, and JS OOP fundamentals. `Principles-of-OOP-JavaScript.pdf` is a published book.

### F. Software Engineering & System Design (`Software-Engineering/`, `System-Design/`)
* **Files Present:**
  * `System-Design/System-Design-Cheatsheet.md` (9.1 KB) — Machine-readable Markdown. Attributed explicitly to `https://cheatsheet.dennyzhang.com/cheatsheet-systemdesign-A4`.
  * `SE-Interview-Questions.pdf` (809 KB), `Software-Engineering.pdf` (2.3 MB).
* **Audit Findings:** Denny Zhang cheatsheet contains excellent system design question prompts (e.g., Rate Limiter, Twitter feed, Distributed Counter).

### G. HR & Behavioral
* **Files Present:**
  * `HR-Interview-Questions.pdf` (318 KB)
  * `25-Job-Interview-Preparation-Prompts.md` (2.2 KB) — Attributed to YouTube channel *Lets Code*.
* **Audit Findings:** Generic ChatGPT prompts rather than structured questions.

---

## 4. Schema Compatibility Analysis (19-Field Pipeline Schema)

Our production MLOps pipeline enforces the documented 19-field schema (`src/data/validation.py`). Here is how content from `Krishnagangwal/CS-Fundamentals` maps to this schema:

| Schema Field | Available in Source? | Can Be Extracted Reliably? | Status & Requirement in Pipeline |
| :--- | :---: | :---: | :--- |
| `question_id` | No | Yes | **Generated systematically** (e.g. `Q_CN_001`, `Q_OS_001`). |
| `domain` | Implicit | Yes | **Mapped to approved domain** (e.g. `Computer Networks`, `Operating Systems`). |
| `difficulty` | No | Partial | **Curated manually** (`Easy`, `Medium`, `Hard`) based on question depth. |
| `question_type` | No | Yes | **Classified manually** (`Conceptual`, `Comparative`, `Diagnostic`, `Behavioral / HR`). |
| `question` | **Yes** | **Yes** | **Extracted directly** from question banks and cheatsheets. |
| `reference_answer` | Partial | Partial | **Extracted / drafted**, but must be verified against course curriculum. |
| `expected_concepts`| No | No | **Must be curated** (semicolon-delimited list of mandatory technical terms). |
| `candidate_answer` | **NO** | **NO** | **COMPLETELY MISSING.** Must be collected from mock interviews or generated as controlled variants. |
| `correctness_score`| **NO** | **NO** | **COMPLETELY MISSING.** Requires human rubric annotation ($0-5$). |
| `completeness_score`| **NO** | **NO** | **COMPLETELY MISSING.** Requires human rubric annotation ($0-5$). |
| `communication_score`| **NO** | **NO** | **COMPLETELY MISSING.** Requires human rubric annotation ($0-5$). |
| `total_score` | **NO** | **NO** | **COMPLETELY MISSING.** Computed as sum of human dimensional scores ($0-15$). |
| `quality_label` | **NO** | **NO** | **COMPLETELY MISSING.** Proposed tier ($0, 1, 2, 3$) mapped from human total score. |
| `source` | Yes | Yes | Populated as `Krishnagangwal/CS-Fundamentals`. |
| `source_license` | **NO** | **NO** | **UNLICENSED.** Must be documented as `UNLICENSED / FAIR-USE PROMPTS ONLY`. |
| `annotator_id` | No | No | Set during human evaluation (e.g. `ANN_01`). |
| `annotation_method`| No | No | Set during human evaluation (e.g. `human_rubric_adjudicated`). |
| `version` | No | Yes | Set to dataset semantic version (e.g. `v0.1.0`). |
| `split_group` | No | Yes | Set to `question_id` to guarantee zero cross-partition leakage. |

---

## 5. Critical MLOps Distinction: Question Bank vs. Classifier Training Dataset

$$\text{Supervised Training Data} = \{(\mathbf{x}_i, y_i)\}_{i=1}^N$$
$$\text{Input } \mathbf{x}_i = \text{Text}(\text{Question}_i, \text{Candidate Answer}_i)$$
$$\text{Target } y_i \in \{0: \text{Poor}, 1: \text{Needs Improvement}, 2: \text{Good}, 3: \text{Excellent}\}$$

* **What `CS-Fundamentals` provides:** Question prompts and reference answers ($\text{Question}, \text{Domain}, \text{Ref. Answer}$).
* **What `CS-Fundamentals` lacks:** Candidate responses of varying quality and corresponding ground-truth scores ($\text{Candidate Answer}, y$).
* **Conclusion:** You cannot train or evaluate the 4-tier answer quality classifier using `CS-Fundamentals` alone without fabricating candidate answers and labels. Doing so would violate academic integrity and produce a scientifically invalid model.

---

## 6. Pilot Extraction Strategy (Proposed)

If approved by faculty for question bank seeding:
1. **Pilot Scope:** Extract a controlled sample of **12 questions** strictly from machine-readable Markdown files:
   * 4 Computer Networks questions from `Computer-Network-Notes-for-Placements-and-GATE.md`.
   * 4 Operating Systems questions from `Operating-System/README.md`.
   * 4 System Design / Software Engineering questions from `System-Design-Cheatsheet.md`.
2. **Exclusion of Binary Files:** Do not parse or store the 270 MB of binary PDFs or DOCX files in Git or DVC.
3. **Question Bank Seeding Only:** Ingest extracted questions into a dedicated question-bank schema (`data/question_bank/`) rather than forcing them into the 19-field labeled dataset table.

---

## 7. Recommended Next Step

**Do NOT attempt full dataset ingestion or classifier training on this repository.**  
Present this audit to your course faculty advisor alongside [`docs/dataset/DATASET_APPROVAL.md`](DATASET_APPROVAL.md) to formally confirm:
1. Approval of question prompts sourced from open curricula and verified repositories.
2. The approved protocol for gathering or drafting candidate responses across proficiency tiers.
3. Human rubric calibration before assembling `data/raw/interview_data.csv`.
