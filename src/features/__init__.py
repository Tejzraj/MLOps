"""Feature extraction, vectorization, and text processing module.

Transforms raw question-answer text pairs into vectorized numerical
representations (TF-IDF, linguistic features, embeddings) for ML models.
"""

from src.features.build_features import (
    FEATURE_INPUT_COLUMNS,
    TARGET_COLUMN,
    build_features,
    create_vectorizer,
    fit_feature_pipeline,
    prepare_text_corpus,
    transform_features,
)

__all__ = [
    "FEATURE_INPUT_COLUMNS",
    "TARGET_COLUMN",
    "build_features",
    "create_vectorizer",
    "fit_feature_pipeline",
    "prepare_text_corpus",
    "transform_features",
]
