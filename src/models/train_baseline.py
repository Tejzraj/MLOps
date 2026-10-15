"""Baseline model training stage for Phase 1 MLOps pipeline.

Trains Logistic Regression baseline (and optional Random Forest comparison)
on TF-IDF features with MLflow experiment tracking and model artifact serialization.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

# Ensure project root is in sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import joblib
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from src.features.build_features import transform_features
from src.utils.config import compute_data_fingerprint, get_logger, load_config, load_params

logger = get_logger("src.models.train_baseline")

ALLOWED_TARGET_CLASSES = (0, 1, 2, 3)
CLASS_NAMES = {
    0: "Poor",
    1: "Needs Improvement",
    2: "Good",
    3: "Excellent",
}


def build_classifier(
    algorithm: str = "logistic_regression",
    model_params: dict[str, Any] | None = None,
) -> LogisticRegression | RandomForestClassifier:
    """Instantiates a classifier based on algorithm name and hyperparameters.

    Args:
        algorithm: 'logistic_regression' or 'random_forest'.
        model_params: Dictionary of hyperparameters from params.yaml.

    Returns:
        Configured scikit-learn classifier instance.

    Raises:
        ValueError: If algorithm name is unsupported.
    """
    params = model_params or {}

    if algorithm == "logistic_regression":
        c_param = float(params.get("c_param", 1.0))
        solver = str(params.get("solver", "lbfgs"))
        max_iter = int(params.get("max_iter", 1000))
        random_state = int(params.get("random_state", 42))

        logger.info(
            f"Configuring LogisticRegression: C={c_param}, solver='{solver}', "
            f"max_iter={max_iter}, random_state={random_state}"
        )
        return LogisticRegression(
            C=c_param,
            solver=solver,
            max_iter=max_iter,
            random_state=random_state,
        )

    elif algorithm == "random_forest":
        n_estimators = int(params.get("n_estimators", 100))
        max_depth = params.get("max_depth", 15)
        if max_depth is not None:
            max_depth = int(max_depth)
        random_state = int(params.get("random_state", 42))

        logger.info(
            f"Configuring RandomForestClassifier: n_estimators={n_estimators}, "
            f"max_depth={max_depth}, random_state={random_state}"
        )
        return RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
        )

    else:
        raise ValueError(
            f"Unsupported algorithm '{algorithm}'. Must be 'logistic_regression' or 'random_forest'."
        )


def validate_training_data(
    train_df: pd.DataFrame, target_column: str = "quality_label"
) -> np.ndarray:
    """Validates that training data contains valid target classes and sufficient data.

    Args:
        train_df: Training DataFrame.
        target_column: Target column name ('domain' or 'quality_label').

    Returns:
        NumPy array of target labels.

    Raises:
        ValueError: If target column is missing, has invalid classes, or has < 2 unique classes.
    """
    if target_column not in train_df.columns:
        raise ValueError(
            f"Target column '{target_column}' missing from training DataFrame. "
            f"Available: {list(train_df.columns)}."
        )

    y = train_df[target_column].to_numpy()
    unique_classes = np.unique(y)

    if target_column == "domain":
        from src.data.validation import QUESTION_BANK_DOMAINS

        allowed: set[Any] = set(QUESTION_BANK_DOMAINS)
    else:
        allowed = set(ALLOWED_TARGET_CLASSES)

    invalid_classes = [c for c in unique_classes if c not in allowed]
    if invalid_classes:
        raise ValueError(
            f"Training data contains invalid target classes: {invalid_classes}. "
            f"Allowed classes: {sorted(str(c) for c in allowed)}."
        )

    if len(unique_classes) < 2:
        raise ValueError(
            f"Training data contains only {len(unique_classes)} class ({unique_classes}). "
            "At least 2 distinct classes are required to train a classification model."
        )

    logger.info(
        f"Target data validated: {len(y)} samples across {len(unique_classes)} classes: "
        f"{dict(pd.Series(y).value_counts())}."
    )
    return y


def setup_mlflow_tracking(
    config_path: str | Path | None = None,
) -> tuple[str, str]:
    """Initializes MLflow tracking URI and experiment name from configs/config.yaml.

    Args:
        config_path: Optional path to config.yaml.

    Returns:
        Tuple of (tracking_uri, experiment_name).
    """
    import os

    os.environ.setdefault("MLFLOW_ALLOW_FILE_STORE", "true")

    try:
        cfg = load_config(config_path or "configs/config.yaml")
        mlflow_cfg = cfg.get("mlflow", {})
        tracking_uri = mlflow_cfg.get("tracking_uri", "mlruns")
        experiment_name = mlflow_cfg.get("experiment_name", "interview-answer-quality-baseline")
    except Exception as exc:
        logger.warning(
            f"Could not load MLflow configuration ({exc}). Using defaults: tracking_uri='mlruns'."
        )
        tracking_uri = "mlruns"
        experiment_name = "interview-answer-quality-baseline"

    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)
    logger.info(
        f"MLflow initialized: tracking_uri='{tracking_uri}', experiment='{experiment_name}'."
    )
    return tracking_uri, experiment_name


def train_model(
    train_path: str | Path,
    vectorizer_path: str | Path,
    output_model_path: str | Path,
    algorithm: str = "logistic_regression",
    model_params: dict[str, Any] | None = None,
    track_with_mlflow: bool = True,
    target_column: str | None = None,
) -> Any:
    """Loads training data, featurizes it, trains model, logs to MLflow, and saves artifact.

    Args:
        train_path: Path to processed train.parquet.
        vectorizer_path: Path to fitted models/tfidf_vectorizer.joblib.
        output_model_path: Path to save models/baseline_model.joblib.
        algorithm: 'logistic_regression' or 'random_forest'.
        model_params: Model hyperparameters dictionary.
        track_with_mlflow: Whether to log run to MLflow.
        target_column: Target column name ('domain' or 'quality_label').

    Returns:
        Trained model instance.

    Raises:
        FileNotFoundError: If train data or vectorizer artifact does not exist.
        ValueError: If training data validation fails.
    """
    train_file = Path(train_path)
    vec_file = Path(vectorizer_path)
    out_file = Path(output_model_path)

    if not train_file.is_file():
        raise FileNotFoundError(
            f"Processed training set not found at '{train_file.resolve()}'. "
            "Please run the preprocess stage first."
        )
    if not vec_file.is_file():
        raise FileNotFoundError(
            f"Fitted vectorizer artifact not found at '{vec_file.resolve()}'. "
            "Please run the feature_engineering stage first."
        )

    logger.info(f"Loading training data from '{train_file}'...")
    train_df = pd.read_parquet(train_file)
    fingerprint = compute_data_fingerprint(train_df)

    target_col = target_column or ("domain" if "domain" in train_df.columns else "quality_label")
    y_train = validate_training_data(train_df, target_column=target_col)

    logger.info(f"Loading fitted vectorizer from '{vec_file}'...")
    vectorizer = joblib.load(vec_file)

    logger.info("Transforming training texts into TF-IDF feature matrix...")
    x_train, _ = transform_features(train_df, vectorizer, target_column=target_col)
    logger.info(f"Feature matrix shape: {x_train.shape}.")

    clf = build_classifier(algorithm=algorithm, model_params=model_params)

    # Train model
    logger.info(f"Training {algorithm} model on {x_train.shape[0]} samples...")
    clf.fit(x_train, y_train)
    logger.info("Model fitting complete.")

    # Save model artifact and metadata bundle
    out_file.parent.mkdir(parents=True, exist_ok=True)
    metadata = {
        "algorithm": algorithm,
        "model_params": model_params or {},
        "target_column": target_col,
        "train_fingerprint": fingerprint,
        "n_train_samples": int(x_train.shape[0]),
        "n_features": int(x_train.shape[1]),
        "classes": [int(c) if isinstance(c, (int, np.integer)) else str(c) for c in clf.classes_],
    }
    artifact_bundle = {
        "model": clf,
        "metadata": metadata,
    }
    joblib.dump(artifact_bundle, out_file)
    logger.info(f"Saved trained model artifact bundle to '{out_file}'.")

    # MLflow Tracking
    if track_with_mlflow:
        setup_mlflow_tracking()
        run_name = f"{algorithm}_baseline"
        with mlflow.start_run(run_name=run_name):
            mlflow.log_param("algorithm", algorithm)
            mlflow.log_param("train_samples", int(x_train.shape[0]))
            mlflow.log_param("n_features", int(x_train.shape[1]))
            mlflow.log_param("train_data_fingerprint", fingerprint[:16])

            if model_params:
                for param_name, param_val in model_params.items():
                    mlflow.log_param(param_name, param_val)

            # Log scikit-learn model artifact
            try:
                mlflow.sklearn.log_model(
                    clf, artifact_path="model", pip_requirements=["scikit-learn"]
                )
            except Exception as exc:
                logger.warning(f"Could not log sklearn model to MLflow: {exc}")

            logger.info("Successfully logged parameters and model to MLflow.")

    return clf


def main() -> None:
    """CLI entrypoint for DVC train_baseline stage."""
    parser = argparse.ArgumentParser(description="Train baseline classification model.")
    parser.add_argument(
        "--train-data",
        type=str,
        default="data/processed/train.parquet",
        help="Path to training Parquet split.",
    )
    parser.add_argument(
        "--vectorizer",
        type=str,
        default="models/tfidf_vectorizer.joblib",
        help="Path to fitted TF-IDF vectorizer artifact.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="models/baseline_model.joblib",
        help="Path to save trained model artifact.",
    )
    parser.add_argument(
        "--algorithm",
        type=str,
        default=None,
        help="Model algorithm ('logistic_regression' or 'random_forest').",
    )
    args = parser.parse_args()

    params = load_params()
    model_cfg = params.get("model", {})
    algorithm = args.algorithm or model_cfg.get("baseline", {}).get(
        "algorithm", "logistic_regression"
    )

    if algorithm == "logistic_regression":
        model_params = model_cfg.get("baseline", {})
    else:
        model_params = model_cfg.get("comparison", {})

    target_column = params.get("data", {}).get("target_column")

    train_model(
        train_path=args.train_data,
        vectorizer_path=args.vectorizer,
        output_model_path=args.output,
        algorithm=algorithm,
        model_params=model_params,
        track_with_mlflow=True,
        target_column=target_column,
    )


if __name__ == "__main__":
    main()
