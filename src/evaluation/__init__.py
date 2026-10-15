"""Model evaluation, metrics computation, and error analysis module.

Calculates multi-class classification metrics (accuracy, weighted/macro F1,
precision, recall), generates confusion matrices, and outputs evaluation reports.
"""

from src.evaluation.evaluate import (
    ALL_CLASSES,
    CLASS_LABELS,
    compute_evaluation_metrics,
    evaluate_model,
    extract_misclassified_examples,
    plot_confusion_matrix,
)

__all__ = [
    "ALL_CLASSES",
    "CLASS_LABELS",
    "compute_evaluation_metrics",
    "evaluate_model",
    "extract_misclassified_examples",
    "plot_confusion_matrix",
]
