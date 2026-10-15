"""Unit tests for model evaluation, metrics calculation, and confusion matrix plotting.

Uses artificial in-memory arrays and DataFrames.
"""

from __future__ import annotations

import json

import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from src.evaluation.evaluate import (
    ALL_CLASSES,
    compute_evaluation_metrics,
    evaluate_model,
    extract_misclassified_examples,
    plot_confusion_matrix,
)


def test_compute_evaluation_metrics_explicit_classes() -> None:
    """Verifies that evaluation metrics produce a 4x4 confusion matrix with [0, 1, 2, 3] labels."""
    y_true = np.array([0, 1, 2, 3, 0, 1, 2, 3])
    y_pred = np.array([0, 1, 2, 3, 1, 1, 2, 2])

    metrics = compute_evaluation_metrics(y_true, y_pred, classes=ALL_CLASSES)

    assert "accuracy" in metrics
    assert "f1_weighted" in metrics
    assert "f1_macro" in metrics
    assert "precision_weighted" in metrics
    assert "recall_weighted" in metrics
    assert metrics["classes"] == [0, 1, 2, 3]

    cm = metrics["confusion_matrix"]
    assert len(cm) == 4  # 4 rows
    assert len(cm[0]) == 4  # 4 columns

    # Perfect predictions for class 0 (1 correct, 1 predicted as 1)
    assert cm[0][0] == 1
    assert cm[0][1] == 1


def test_plot_confusion_matrix(tmp_path: pytest.TempPathFactory) -> None:
    """Verifies confusion matrix plotting saves a non-empty image file."""
    cm = [[2, 0, 0, 0], [0, 3, 0, 0], [0, 0, 1, 1], [0, 0, 0, 4]]
    fig_path = tmp_path / "confusion_matrix.png"

    saved_path = plot_confusion_matrix(cm, fig_path, classes=ALL_CLASSES)
    assert saved_path.is_file()
    assert saved_path.stat().st_size > 0


def test_extract_misclassified_examples_sanitization() -> None:
    """Verifies misclassified instances exclude PII and sensitive info."""
    df = pd.DataFrame(
        [
            {
                "question_id": "Q_001",
                "domain": "OS",
                "difficulty": "Easy",
                "question": "What is a process?",
                "candidate_answer": "A running program.",
                "annotator_id": "SECRET_PII_ANN_01",
                "source_license": "Apache-2.0",
            },
            {
                "question_id": "Q_002",
                "domain": "OS",
                "difficulty": "Medium",
                "question": "What is a thread?",
                "candidate_answer": "A lightweight process.",
                "annotator_id": "SECRET_PII_ANN_02",
                "source_license": "Apache-2.0",
            },
        ]
    )

    y_true = np.array([1, 2])
    y_pred = np.array([0, 2])  # Row 0 is misclassified

    errors = extract_misclassified_examples(df, y_true, y_pred)
    assert len(errors) == 1
    err = errors[0]

    assert err["question_id"] == "Q_001"
    assert err["true_label"] == 1
    assert err["predicted_label"] == 0
    # Annotator ID or internal tokens must NOT be present
    assert "annotator_id" not in err


def test_evaluate_model_end_to_end(tmp_path: pytest.TempPathFactory) -> None:
    """Verifies evaluate_model loads test Parquet and model bundle, exports metrics and figure."""
    test_parquet = tmp_path / "test.parquet"
    vec_path = tmp_path / "vec.joblib"
    mod_path = tmp_path / "model.joblib"
    metrics_path = tmp_path / "metrics.json"
    fig_path = tmp_path / "cm.png"

    test_df = pd.DataFrame(
        [
            {"question": "Q1", "candidate_answer": "A1", "quality_label": 0},
            {"question": "Q2", "candidate_answer": "A2", "quality_label": 1},
            {"question": "Q3", "candidate_answer": "A3", "quality_label": 2},
            {"question": "Q4", "candidate_answer": "A4", "quality_label": 3},
        ]
    )
    test_df.to_parquet(test_parquet, index=False)

    vec = TfidfVectorizer(min_df=1)
    corpus = (test_df["question"] + " " + test_df["candidate_answer"]).tolist()
    x = vec.fit_transform(corpus)
    joblib.dump(vec, vec_path)

    clf = LogisticRegression(random_state=42)
    clf.fit(x, test_df["quality_label"])
    bundle = {"model": clf, "metadata": {"algorithm": "logistic_regression"}}
    joblib.dump(bundle, mod_path)

    results = evaluate_model(
        test_path=test_parquet,
        model_path=mod_path,
        vectorizer_path=vec_path,
        metrics_output_path=metrics_path,
        figure_output_path=fig_path,
        track_with_mlflow=True,
    )

    assert metrics_path.is_file()
    assert fig_path.is_file()
    assert "accuracy" in results
    assert results["n_test_samples"] == 4

    with metrics_path.open() as f:
        loaded = json.load(f)
    assert loaded["classes"] == [0, 1, 2, 3]
