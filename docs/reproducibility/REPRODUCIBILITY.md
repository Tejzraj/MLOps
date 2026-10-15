# Reproducibility Guide & Verification Handbook

> **Project:** AI-Based Interview Preparation Assistant  
> **Course:** AI252TA – Machine Learning Operations | Semester V  
> **Repository:** [https://github.com/Tejzraj/MLOps.git](https://github.com/Tejzraj/MLOps.git)  
> **Last Verified:** 2026-10-15  
> **Reproducibility Status:** Code & Test Suite Verified (100% Passing) | Pipeline Execution Blocked on Input Data  

---

## 1. Executive Summary

This handbook details the end-to-end reproducibility protocol for the **AI-Based Interview Preparation Assistant**. It provides explicit instructions for reproducing the test suite, code quality checks, and DVC pipeline from a clean repository checkout.

### Reproducibility State Declaration
* **Pipeline Code & Architecture:** **100% Implemented & Offline-Tested** (51 automated unit tests passing, 85% code coverage).
* **Code Quality & Static Analysis:** **100% Passing** (Ruff linter clean, Black formatting clean, zero git whitespace defects).
* **Pipeline DAG:** **100% Validated** (`dvc dag` resolves all 5 stages in proper topological order).
* **Real-Data Execution (`dvc repro`):** **Intentionally Blocked** pending faculty approval and placement of `data/raw/interview_data.csv`. The pipeline refuses to execute on fabricated or unverified candidate responses.

---

## 2. Environment Specifications

| Component | Tested Version | Verification Command |
| :--- | :--- | :--- |
| **Operating System** | macOS 15.3 (Darwin 24.3.0) / Linux | `uname -a` |
| **Python** | `3.11.9` | `python --version` |
| **DVC (Data Version Control)**| `3.67.1` | `dvc --version` |
| **MLflow Tracking** | `3.16.1` | `mlflow --version` |
| **PyTest** | `9.1.1` (with `pytest-cov 5.0.0`) | `pytest --version` |
| **Scikit-Learn** | `1.6.0` | `python -c "import sklearn; print(sklearn.__version__)"` |
| **Pandas** | `2.2.3` | `python -c "import pandas; print(pandas.__version__)"` |
| **Random State Pinning** | `42` (configured across all stages in `params.yaml`) | `params.yaml` |

---

## 3. Step-by-Step Reproduction Guide (From Clean Checkout)

Follow these exact steps to verify the project on a new workstation:

### Step 1: Clone & Checkout
```bash
git clone https://github.com/Tejzraj/MLOps.git
cd MLOps
git checkout main
```

### Step 2: Environment Setup
```bash
# Initialize virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Upgrade packaging tools and install production + dev dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Step 3: Run Automated Test Suite
The test suite operates entirely in memory using synthetic fixtures and requires no internet access or external files:

```bash
# Run all 51 automated unit tests with full statement coverage
pytest tests/
```
*Expected Outcome:* `51 passed in ~13s` with $\ge 80\%$ total statement coverage on `src/`.

### Step 4: Verify Linting & Formatting
```bash
# Verify static analysis rules
ruff check src/ tests/

# Verify code formatting
black --check src/ tests/

# Verify git diff formatting
git diff --check
```
*Expected Outcome:* Zero linter violations, zero formatting changes needed, zero trailing whitespace errors.

### Step 5: Verify DVC Pipeline DAG
```bash
# Inspect the topological dependency graph
dvc dag
```
*Expected Output:*
```text
                                  +-----------+                         
                                  | load_data |                         
                                  +-----------+                         
                                         *                              
                                         *                              
                                         *                              
                                  +------------+                        
                                  | preprocess |*                       
                             *****+------------+ *****                  
                        *****            *            *****             
                   *****                  *                ****         
                ***                       *                    *****    
+---------------------+                   *                         *** 
| feature_engineering |                   *                           * 
+---------------------+**                 *                           * 
            *            *****            *                           * 
            *                 *****       *                           * 
            *                      ***    *                           * 
            ***                  +----------------+                 *** 
               *****             | train_baseline |            *****    
                    *****        +----------------+        ****         
                         ****             *           *****             
                             *****       *       *****                  
                                  ***    *    ***                       
                                   +----------+                         
                                   | evaluate |                         
                                   +----------+                         
```

### Step 6: Test Data-Missing Guardrail
```bash
# Test pipeline behavior when raw data is not yet present
dvc repro
```
*Expected Outcome:* Clean, explicit halt at stage `load_data`:
```text
ERROR: failed to reproduce 'load_data': No such file or directory: '.../data/raw/interview_data.csv'
```

### Step 7: Executing with Approved Data (When Available)
Once the faculty committee approves the dataset dossier:
```bash
# 1. Place the approved dataset CSV at:
cp /path/to/approved_data.csv data/raw/interview_data.csv

# 2. Track with DVC
dvc add data/raw/interview_data.csv

# 3. Reproduce the entire pipeline end-to-end
dvc repro

# 4. Re-run to verify DVC cache hit (no stages re-executed)
dvc repro
```
*Expected Outcome on re-run:* `Data and pipelines are up to date.`

### Step 8: View MLflow Experiment Tracking
```bash
# Launch MLflow tracking server locally
mlflow ui --port 5000
# Open http://localhost:5000 in your browser
```
*Expected Dashboard Content:* Experiment `interview-answer-quality-baseline` recording run parameters, model artifacts, metrics, and confusion matrix plots.

---

## 4. DVC Pipeline Stage Reference

| Stage | Command | Dependencies | Parameters | Outputs & Metrics | Cache |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **`load_data`** | `python src/data/load_data.py` | `data/raw/interview_data.csv`, `src/data/load_data.py`, `src/data/validation.py`, `src/utils/config.py` | `data.raw_data_path` | `data/interim/loaded_data.parquet` | True |
| **`preprocess`** | `python src/data/preprocess.py` | `data/interim/loaded_data.parquet`, `src/data/preprocess.py`, `src/utils/config.py` | `split.test_size`, `split.validation_size`, `split.random_state` | `data/processed/train.parquet`, `val.parquet`, `test.parquet` | True |
| **`feature_engineering`** | `python src/features/build_features.py` | `data/processed/train.parquet`, `src/features/build_features.py`, `src/utils/config.py` | `features.tfidf.*` | `models/tfidf_vectorizer.joblib` | True |
| **`train_baseline`** | `python src/models/train_baseline.py` | `data/processed/train.parquet`, `models/tfidf_vectorizer.joblib`, `src/models/train_baseline.py`, `src/features/build_features.py`, `src/utils/config.py` | `model.baseline.*` | `models/baseline_model.joblib` | True |
| **`evaluate`** | `python src/evaluation/evaluate.py` | `data/processed/test.parquet`, `models/baseline_model.joblib`, `models/tfidf_vectorizer.joblib`, `src/evaluation/evaluate.py`, `src/features/build_features.py`, `src/utils/config.py` | `evaluation.primary_metric` | `reports/metrics.json` (metric), `reports/figures/confusion_matrix.png` (plot) | False |

---

## 5. DVC Remote Configuration (Production Deployment Guide)

The repository currently utilizes **local DVC tracking** for offline development. To establish a remote artifact cache for multi-developer collaboration or cloud CI/CD:

### Option A: Local / Network Shared Directory Remote
```bash
mkdir -p /path/to/shared_dvc_storage
dvc remote add -d local_remote /path/to/shared_dvc_storage
dvc push
```

### Option B: AWS S3 Remote
```bash
dvc remote add -d s3_remote s3://my-mlops-bucket/interview-assistant
dvc remote modify s3_remote region ap-south-1
dvc push
```

### Option C: Google Cloud Storage Remote
```bash
dvc remote add -d gcs_remote gs://my-mlops-bucket/interview-assistant
dvc push
```
*(Pointer metadata in `.dvc/config` is committed to Git; data payloads remain in the remote bucket).*

---

## 6. Audit & Defense Checklist for Faculty Viva

- [x] **Zero Target Leakage:** Features use exclusively `question` and `candidate_answer`; target scores and metadata are strictly excluded.
- [x] **Zero Question Leakage:** `GroupShuffleSplit` by `question_id` guarantees test questions are completely unseen during training.
- [x] **Strict Offline Determinism:** Random seeds pinned to `42`; all vectorizers fit strictly on training splits.
- [x] **Zero PII Exposure:** Misclassified error logs scrub annotator tokens and personal identifiers.
- [x] **Zero Fabricated Results:** Unverified training runs and fake metrics are strictly prohibited.
