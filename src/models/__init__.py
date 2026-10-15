"""Model architecture, training routines, and inference pipeline.

Encapsulates baseline model trainers (Logistic Regression, Random Forest),
hyperparameter tuning logic, and model serialization with MLflow tracking.
"""

from src.models.train_baseline import (
    ALLOWED_TARGET_CLASSES,
    CLASS_NAMES,
    build_classifier,
    setup_mlflow_tracking,
    train_model,
    validate_training_data,
)

__all__ = [
    "ALLOWED_TARGET_CLASSES",
    "CLASS_NAMES",
    "build_classifier",
    "setup_mlflow_tracking",
    "train_model",
    "validate_training_data",
]
