"""Model evaluation and error analysis stage for Phase 1 MLOps pipeline.

Evaluates trained baseline classifier exclusively on the held-out test split,
computes multi-class classification metrics with explicit [0, 1, 2, 3] class ordering,
exports metrics.json and confusion matrix plot, and logs results to MLflow.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import joblib
import matplotlib
import mlflow
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from src.features.build_features import transform_features
from src.models.train_baseline import setup_mlflow_tracking
from src.utils.config import compute_data_fingerprint, get_logger

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

logger = get_logger("src.evaluation.evaluate")

ALL_CLASSES = [0, 1, 2, 3]
CLASS_LABELS = {
    0: "Poor",
    1: "Needs Improvement",
    2: "Good",
    3: "Excellent",
}


def compute_evaluation_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    classes: list[int] | None = None,
) -> dict[str, Any]:
    """Calculates multi-class classification metrics with explicit class ordering.

    Args:
        y_true: Ground truth target labels.
        y_pred: Model predicted target labels.
        classes: Ordered list of all class IDs (default [0, 1, 2, 3]).

    Returns:
        Dictionary of computed metrics, per-class metrics, and confusion matrix.
    """
    target_classes = classes or ALL_CLASSES

    acc = float(accuracy_score(y_true, y_pred))
    f1_w = float(f1_score(y_true, y_pred, average="weighted", zero_division=0))
    f1_m = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
    prec_w = float(precision_score(y_true, y_pred, average="weighted", zero_division=0))
    rec_w = float(recall_score(y_true, y_pred, average="weighted", zero_division=0))

    # Confusion matrix with explicit labels [0, 1, 2, 3]
    cm = confusion_matrix(y_true, y_pred, labels=target_classes).tolist()

    # Per-class metrics
    per_class_f1 = f1_score(y_true, y_pred, average=None, labels=target_classes, zero_division=0)
    per_class_prec = precision_score(
        y_true, y_pred, average=None, labels=target_classes, zero_division=0
    )
    per_class_rec = recall_score(
        y_true, y_pred, average=None, labels=target_classes, zero_division=0
    )

    per_class_breakdown: dict[str, dict[str, float]] = {}
    for idx, c in enumerate(target_classes):
        label_name = CLASS_LABELS.get(c, str(c))
        per_class_breakdown[f"class_{c}_{label_name}"] = {
            "f1": float(per_class_f1[idx]),
            "precision": float(per_class_prec[idx]),
            "recall": float(per_class_rec[idx]),
        }

    return {
        "accuracy": round(acc, 4),
        "f1_weighted": round(f1_w, 4),
        "f1_macro": round(f1_m, 4),
        "precision_weighted": round(prec_w, 4),
        "recall_weighted": round(rec_w, 4),
        "confusion_matrix": cm,
        "classes": target_classes,
        "per_class": per_class_breakdown,
    }


def plot_confusion_matrix(
    cm: list[list[int]],
    output_path: str | Path,
    classes: list[int] | None = None,
) -> Path:
    """Generates and saves a confusion matrix visualization using matplotlib.

    Args:
        cm: Confusion matrix 2D list.
        output_path: Path to output PNG image.
        classes: Ordered list of class IDs.

    Returns:
        Path to the saved PNG image.
    """
    target_classes = classes or ALL_CLASSES
    labels = [f"{c}: {CLASS_LABELS.get(c, '')}" for c in target_classes]
    matrix = np.array(cm)

    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(matrix, interpolation="nearest", cmap=plt.cm.Oranges)
    fig.colorbar(im, ax=ax)

    ax.set(
        xticks=np.arange(len(labels)),
        yticks=np.arange(len(labels)),
        xticklabels=labels,
        yticklabels=labels,
        ylabel="True Label",
        xlabel="Predicted Label",
        title="Confusion Matrix (Baseline Classifier)",
    )

    plt.setp(ax.get_xticklabels(), rotation=35, ha="right", rotation_mode="anchor")

    # Annotate counts inside cells
    thresh = matrix.max() / 2.0 if matrix.max() > 0 else 1.0
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(
                j,
                i,
                format(matrix[i, j], "d"),
                ha="center",
                va="center",
                color="white" if matrix[i, j] > thresh else "black",
            )

    fig.tight_layout()
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_file, dpi=150)
    plt.close(fig)

    logger.info(f"Saved confusion matrix figure to '{out_file}'.")
    return out_file


def extract_misclassified_examples(
    df: pd.DataFrame,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    max_examples: int = 5,
) -> list[dict[str, Any]]:
    """Extracts misclassified instances with PII and sensitive info excluded.

    Args:
        df: Test DataFrame.
        y_true: Ground truth array.
        y_pred: Predicted array.
        max_examples: Maximum misclassified samples to collect.

    Returns:
        List of sanitized error records.
    """
    errors: list[dict[str, Any]] = []
    mis_idx = np.where(y_true != y_pred)[0]

    for idx in mis_idx[:max_examples]:
        row = df.iloc[idx]
        errors.append(
            {
                "question_id": str(row.get("question_id", "UNKNOWN")),
                "domain": str(row.get("domain", "UNKNOWN")),
                "difficulty": str(row.get("difficulty", "UNKNOWN")),
                "true_label": int(y_true[idx]),
                "predicted_label": int(y_pred[idx]),
                "question_preview": str(row.get("question", ""))[:80],
                "candidate_answer_preview": str(row.get("candidate_answer", ""))[:80],
            }
        )

    return errors


def evaluate_model(
    test_path: str | Path,
    model_path: str | Path,
    vectorizer_path: str | Path,
    metrics_output_path: str | Path = "reports/metrics.json",
    figure_output_path: str | Path = "reports/figures/confusion_matrix.png",
    track_with_mlflow: bool = True,
) -> dict[str, Any]:
    """Loads test split and model, evaluates predictions, writes reports, and logs to MLflow.

    Args:
        test_path: Path to processed test.parquet.
        model_path: Path to models/baseline_model.joblib.
        vectorizer_path: Path to models/tfidf_vectorizer.joblib.
        metrics_output_path: Path to save reports/metrics.json.
        figure_output_path: Path to save confusion matrix image.
        track_with_mlflow: Whether to log evaluation metrics to MLflow.

    Returns:
        Dictionary of evaluation results.

    Raises:
        FileNotFoundError: If any required input artifact does not exist.
        ValueError: If test set is empty or missing target column.
    """
    test_file = Path(test_path)
    mod_file = Path(model_path)
    vec_file = Path(vectorizer_path)
    metrics_file = Path(metrics_output_path)
    fig_file = Path(figure_output_path)

    for path, desc in [
        (test_file, "Test dataset"),
        (mod_file, "Trained model artifact"),
        (vec_file, "Fitted vectorizer artifact"),
    ]:
        if not path.is_file():
            raise FileNotFoundError(
                f"{desc} not found at '{path.resolve()}'. Please complete upstream pipeline stages first."
            )

    logger.info(f"Loading held-out test data from '{test_file}'...")
    test_df = pd.read_parquet(test_file)
    if test_df.empty:
        raise ValueError("Test DataFrame is empty (0 samples).")
    if "quality_label" not in test_df.columns:
        raise ValueError("Test DataFrame missing 'quality_label' column.")

    y_true = test_df["quality_label"].to_numpy(dtype=int)
    fingerprint = compute_data_fingerprint(test_df)

    logger.info(f"Loading vectorizer from '{vec_file}'...")
    vectorizer = joblib.load(vec_file)

    logger.info(f"Loading model bundle from '{mod_file}'...")
    bundle = joblib.load(mod_file)
    clf = bundle["model"] if isinstance(bundle, dict) and "model" in bundle else bundle

    logger.info(f"Transforming {len(test_df)} test samples...")
    x_test, _ = transform_features(test_df, vectorizer)

    logger.info("Computing predictions on test set...")
    y_pred = clf.predict(x_test)

    # Compute evaluation metrics
    results = compute_evaluation_metrics(y_true, y_pred, classes=ALL_CLASSES)
    results["n_test_samples"] = int(len(test_df))
    results["test_data_fingerprint"] = fingerprint
    results["misclassified_examples"] = extract_misclassified_examples(test_df, y_true, y_pred)

    # Export metrics.json
    metrics_file.parent.mkdir(parents=True, exist_ok=True)
    with metrics_file.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Saved evaluation metrics to '{metrics_file}'.")

    # Plot confusion matrix
    plot_confusion_matrix(results["confusion_matrix"], fig_file, classes=ALL_CLASSES)

    # MLflow Tracking
    if track_with_mlflow:
        setup_mlflow_tracking()
        with mlflow.start_run(run_name="baseline_evaluation"):
            mlflow.log_metric("accuracy", results["accuracy"])
            mlflow.log_metric("f1_weighted", results["f1_weighted"])
            mlflow.log_metric("f1_macro", results["f1_macro"])
            mlflow.log_metric("precision_weighted", results["precision_weighted"])
            mlflow.log_metric("recall_weighted", results["recall_weighted"])
            mlflow.log_param("test_samples", results["n_test_samples"])
            mlflow.log_param("test_data_fingerprint", fingerprint[:16])

            if fig_file.is_file():
                try:
                    mlflow.log_artifact(str(fig_file), artifact_path="evaluation")
                except Exception as exc:
                    logger.warning(f"Could not log confusion matrix artifact to MLflow: {exc}")

            if metrics_file.is_file():
                try:
                    mlflow.log_artifact(str(metrics_file), artifact_path="evaluation")
                except Exception as exc:
                    logger.warning(f"Could not log metrics.json to MLflow: {exc}")

            logger.info("Successfully logged test evaluation metrics to MLflow.")

    return results


def main() -> None:
    """CLI entrypoint for DVC evaluate stage."""
    parser = argparse.ArgumentParser(description="Evaluate baseline model on test data.")
    parser.add_argument(
        "--test-data",
        type=str,
        default="data/processed/test.parquet",
        help="Path to test Parquet split.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="models/baseline_model.joblib",
        help="Path to trained model artifact.",
    )
    parser.add_argument(
        "--vectorizer",
        type=str,
        default="models/tfidf_vectorizer.joblib",
        help="Path to fitted TF-IDF vectorizer artifact.",
    )
    parser.add_argument(
        "--metrics-output",
        type=str,
        default="reports/metrics.json",
        help="Path to save evaluation metrics JSON.",
    )
    parser.add_argument(
        "--figure-output",
        type=str,
        default="reports/figures/confusion_matrix.png",
        help="Path to save confusion matrix PNG.",
    )
    args = parser.parse_args()

    evaluate_model(
        test_path=args.test_data,
        model_path=args.model,
        vectorizer_path=args.vectorizer,
        metrics_output_path=args.metrics_output,
        figure_output_path=args.figure_output,
        track_with_mlflow=True,
    )


if __name__ == "__main__":
    main()
