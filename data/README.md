# Dataset Architecture & Management

> **Course:** AI252TA – Machine Learning Operations | Semester V  
> **Project:** AI-Based Interview Preparation Assistant  
> **Status:** Phase 1 — Dataset Approval In Progress  

---

## 1. Status Notice & Provenance

> **Notice:** Dataset source to be finalized during Phase 1 dataset approval.

No raw data is committed directly to this Git repository. All datasets will be versioned, hashed, and tracked via **Data Version Control (DVC)** once formally reviewed and approved against academic and privacy guidelines.

---

## 2. Dataset Objective & Scope

The purpose of this dataset is to train, evaluate, and benchmark machine learning models that can evaluate the quality of candidate responses given specific technical and behavioral interview questions.

The system addresses **SDG 4 (Quality Education)** and **SDG 8 (Decent Work & Economic Growth)** by providing automated, objective, and reproducible interview coaching feedback.

---

## 3. Expected Schema & Format

The dataset will be structured in tabular format (`.csv` / `.parquet`) with the following schema:

| Column Name | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `question_id` | `string` | Unique identifier for interview question | `"Q_TECH_042"` |
| `domain` | `string` | Interview subject area | `"Data Structures"`, `"System Design"`, `"Behavioral"` |
| `interview_question` | `string` | Full text prompt posed to candidate | `"Explain the difference between a process and a thread."` |
| `candidate_answer` | `string` | Transcribed or typed candidate response | `"A process is an executing instance of a program..."` |
| `quality_label` | `int64` | Target quality classification (0 to 3) | `2` |
| `quality_description` | `string` | Human-readable label tag | `"Good"` |

---

## 4. Quality Label Definitions

The primary ML formulation utilizes a 4-tier ordinal classification framework:

| Class ID | Label | Evaluation Criteria |
| :---: | :--- | :--- |
| **0** | **Poor** | Factually incorrect, incoherent, completely irrelevant, or under 5 words. |
| **1** | **Needs Improvement** | Partially correct but lacks depth, misses crucial technical points, or is poorly structured. |
| **2** | **Good** | Accurate, relevant, covers fundamental concepts correctly with clear explanation. |
| **3** | **Excellent** | Comprehensive, highly articulate, provides practical examples, trade-offs, and edge cases. |

---

## 5. Data Directory Hierarchy

The project adheres to a clean separation of data stages:

```text
data/
├── raw/            # Pristine, immutable raw data dumps (tracked by DVC, ignored by Git)
├── interim/        # Intermediate cleansed and normalized data pairs
├── processed/      # Final train/val/test splits ready for feature extraction & modeling
└── README.md       # Dataset specification and governance documentation
```

*Note: All files under `data/raw/`, `data/interim/`, and `data/processed/` (except `.gitkeep` and documentation) are ignored by Git in `.gitignore`.*

---

## 6. Data Quality Checks & Validation

Before admission into the training pipeline, datasets must pass programmatic checks:
- **Completeness:** Zero null or empty values in `interview_question` or `candidate_answer`.
- **Length Constraints:** Minimum answer token length (e.g., $\ge 5$ tokens) to prevent trivial noise.
- **Class Balance:** Class frequency distribution analysis across all 4 quality tiers.
- **Deduplication:** Removal of exact or near-duplicate QA pairs across splits to avoid data leakage.

---

## 7. Versioning with DVC

Data versioning ensures full experimental reproducibility:
1. Raw data is placed into `data/raw/interview_data.csv`.
2. Tracked via DVC:
   ```bash
   dvc add data/raw/interview_data.csv
   git add data/raw/interview_data.csv.dvc .gitignore
   ```
3. Remote storage (local directory, S3, or GCS) will be configured for artifact persistence.

---

## 8. Privacy, Security & Ethical Considerations

- **Candidate Anonymization:** Datasets must contain strictly anonymized QA pairs. No personally identifiable information (PII) such as candidate names, email addresses, phone numbers, or employer names may be present.
- **Synthetic QA Generation:** If real interview transcripts present privacy hurdles, verified synthetic datasets created under controlled academic rubrics will be utilized.
- **Fairness & Bias:** Lexical evaluation will monitor potential linguistic biases (e.g., non-native speaker phrasing variations).

---

## 9. Future Dataset Expansion

In subsequent phases (Phase 2 & Phase 3), the dataset architecture is planned to accommodate:
- Multi-dimensional scoring (Clarity, Relevance, Completeness, Confidence).
- Audio transcription transcripts with pacing and pause indicators.
- Domain-specific subsets (Software Engineering, Data Science, Product Management).
