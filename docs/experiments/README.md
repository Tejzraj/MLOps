# Experiment Tracking & Benchmarking

> **Project:** AI-Based Interview Preparation Assistant  
> **Course:** AI252TA – Machine Learning Operations | Semester V  
> **Status:** Phase 0 / Phase 1 Inception  

---

## 1. Directory Purpose

This directory records experiment design protocols, hypothesis logs, MLflow run configurations, and benchmark evaluations comparing candidate model architectures.

---

## 2. MLflow Experiment Protocol

All model training executions must log the following metadata to the MLflow tracking server:

1. **Parameters (`params.yaml`):**
   - Feature extraction parameters (`ngram_range`, `max_features`, `sublinear_tf`).
   - Model hyperparameters (regularization `C`, tree estimators, max depth).
   - Data split seeds and stratified distribution ratios.
2. **Metrics:**
   - Primary metric: `f1_weighted`.
   - Secondary metrics: `accuracy`, `precision_weighted`, `recall_weighted`, `f1_macro`.
3. **Artifacts:**
   - Serialized model weights / pipelines (`.joblib`).
   - Confusion matrix visualization plot.
   - Classification report (`classification_report.json`).

---

## 3. Planned Benchmark Logs

- **`baseline_experiments.md`:** Results comparing Logistic Regression baseline against Naive Bayes and Random Forest.
- **`hyperparameter_tuning.md`:** Systematic grid/random search sweeps across feature dimensions and regularizers.
- **`error_analysis.md`:** Qualitative breakdown of misclassified answers (e.g., borderline class 1 vs class 2 responses).
