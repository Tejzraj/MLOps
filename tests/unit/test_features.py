"""Unit tests for feature engineering, leakage prevention, and vectorizer serialization.

Uses artificial in-memory DataFrames for testing.
"""

from __future__ import annotations

import pandas as pd
import pytest

from src.features.build_features import (
    FEATURE_INPUT_COLUMNS,
    TARGET_COLUMN,
    build_features,
    create_vectorizer,
    fit_feature_pipeline,
    prepare_text_corpus,
    transform_features,
)


@pytest.fixture
def feature_sample_df() -> pd.DataFrame:
    """Creates a small DataFrame with text and target labels."""
    return pd.DataFrame(
        [
            {
                "question": "What is virtual memory?",
                "candidate_answer": "Virtual memory is a memory management technique.",
                "quality_label": 2,
                "total_score": 10,
                "annotator_id": "ANN_01",
            },
            {
                "question": "Explain TCP handshake.",
                "candidate_answer": "TCP uses SYN, SYN-ACK, and ACK packets.",
                "quality_label": 3,
                "total_score": 14,
                "annotator_id": "ANN_02",
            },
            {
                "question": "What is deadlock?",
                "candidate_answer": "A condition where threads block each other.",
                "quality_label": 1,
                "total_score": 6,
                "annotator_id": "ANN_01",
            },
        ]
    )


def test_prepare_text_corpus(feature_sample_df: pd.DataFrame) -> None:
    """Verifies that prepare_text_corpus combines question and candidate answer."""
    corpus = prepare_text_corpus(feature_sample_df)
    assert len(corpus) == 3
    assert (
        "What is virtual memory? [SEP] Virtual memory is a memory management technique."
        in corpus[0]
    )


def test_prepare_text_corpus_missing_columns() -> None:
    """Verifies ValueError when required feature columns are missing."""
    df_missing = pd.DataFrame([{"question": "Only question provided."}])
    with pytest.raises(
        ValueError, match="Required input feature column 'candidate_answer' missing"
    ):
        prepare_text_corpus(df_missing)


def test_create_vectorizer_custom_params() -> None:
    """Verifies vectorizer initialization with custom parameters."""
    params = {
        "max_features": 100,
        "ngram_range": [1, 1],
        "stop_words": "english",
        "min_df": 1,
        "sublinear_tf": False,
    }
    vec = create_vectorizer(params)
    assert vec.max_features == 100
    assert vec.ngram_range == (1, 1)
    assert not vec.sublinear_tf


def test_target_leakage_prevention(feature_sample_df: pd.DataFrame) -> None:
    """Verifies feature matrix X does not include target column or metadata."""
    vec = fit_feature_pipeline(feature_sample_df, tfidf_params={"min_df": 1})
    x_matrix, y_labels = transform_features(feature_sample_df, vec)

    # Feature matrix X should only be derived from FEATURE_INPUT_COLUMNS
    assert FEATURE_INPUT_COLUMNS == ["question", "candidate_answer"]
    assert TARGET_COLUMN == "quality_label"

    # Verify target labels extracted separately
    assert y_labels is not None
    assert list(y_labels) == [2, 3, 1]

    # Verify feature matrix shape reflects vocabulary, not extra tabular columns
    assert x_matrix.shape[0] == 3
    assert x_matrix.shape[1] == len(vec.vocabulary_)


def test_build_features_artifact_saved(
    tmp_path: pytest.TempPathFactory, feature_sample_df: pd.DataFrame
) -> None:
    """Verifies build_features loads train data and dumps joblib vectorizer."""
    train_parquet = tmp_path / "train.parquet"
    out_vectorizer = tmp_path / "tfidf_vectorizer.joblib"

    feature_sample_df.to_parquet(train_parquet, index=False)
    vec = build_features(
        train_path=train_parquet,
        output_model_path=out_vectorizer,
        tfidf_params={"min_df": 1},
    )

    assert out_vectorizer.is_file()
    assert len(vec.vocabulary_) > 0
