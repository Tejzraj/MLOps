"""Unit tests for baseline model training, parameter validation, and MLflow logging.

Uses synthetic in-memory fixtures.
"""

from __future__ import annotations

import joblib
import pandas as pd
import pytest
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from src.models.train_baseline import (
    build_classifier,
    train_model,
    validate_training_data,
)


@pytest.fixture
def training_fixture_df() -> pd.DataFrame:
    """Creates a small training dataset with 4 quality classes."""
    return pd.DataFrame(
        [
            {
                "question": "What is paging?",
                "candidate_answer": "Paging is memory.",
                "quality_label": 0,
            },
            {
                "question": "What is paging?",
                "candidate_answer": "Paging splits memory into fixed blocks.",
                "quality_label": 1,
            },
            {
                "question": "What is paging?",
                "candidate_answer": "Paging eliminates external fragmentation using page tables.",
                "quality_label": 2,
            },
            {
                "question": "What is paging?",
                "candidate_answer": "Paging maps virtual pages to physical frames via MMU and page tables.",
                "quality_label": 3,
            },
        ]
    )


def test_build_classifier_logistic_regression() -> None:
    """Verifies Logistic Regression configuration."""
    clf = build_classifier(
        algorithm="logistic_regression",
        model_params={"c_param": 2.5, "solver": "lbfgs", "max_iter": 500, "random_state": 42},
    )
    assert isinstance(clf, LogisticRegression)
    assert clf.C == 2.5
    assert clf.solver == "lbfgs"
    assert clf.max_iter == 500


def test_build_classifier_random_forest() -> None:
    """Verifies Random Forest configuration."""
    clf = build_classifier(
        algorithm="random_forest",
        model_params={"n_estimators": 50, "max_depth": 10, "random_state": 42},
    )
    assert isinstance(clf, RandomForestClassifier)
    assert clf.n_estimators == 50
    assert clf.max_depth == 10


def test_build_classifier_unsupported() -> None:
    """Verifies error on unsupported algorithm."""
    with pytest.raises(ValueError, match="Unsupported algorithm"):
        build_classifier(algorithm="gradient_boosting")


def test_validate_training_data_insufficient_classes() -> None:
    """Verifies ValueError when fewer than 2 distinct classes exist."""
    df_single_class = pd.DataFrame(
        [
            {"quality_label": 1},
            {"quality_label": 1},
        ]
    )
    with pytest.raises(ValueError, match="At least 2 distinct classes are required"):
        validate_training_data(df_single_class)


def test_validate_training_data_invalid_class() -> None:
    """Verifies ValueError when class outside {0, 1, 2, 3} exists."""
    df_bad_class = pd.DataFrame(
        [
            {"quality_label": 1},
            {"quality_label": 99},
        ]
    )
    with pytest.raises(ValueError, match="invalid target classes"):
        validate_training_data(df_bad_class)


def test_train_model_end_to_end_and_mlflow(
    tmp_path: pytest.TempPathFactory, training_fixture_df: pd.DataFrame
) -> None:
    """Verifies train_model fits classifier, serializes artifact bundle, and logs locally."""
    train_parquet = tmp_path / "train.parquet"
    vec_path = tmp_path / "vec.joblib"
    model_path = tmp_path / "baseline_model.joblib"

    # Fit a small vectorizer
    vec = TfidfVectorizer(min_df=1)
    corpus = (
        training_fixture_df["question"] + " " + training_fixture_df["candidate_answer"]
    ).tolist()
    vec.fit(corpus)
    joblib.dump(vec, vec_path)

    training_fixture_df.to_parquet(train_parquet, index=False)

    clf = train_model(
        train_path=train_parquet,
        vectorizer_path=vec_path,
        output_model_path=model_path,
        algorithm="logistic_regression",
        model_params={"c_param": 1.0, "max_iter": 200, "random_state": 42},
        track_with_mlflow=True,
    )

    assert isinstance(clf, LogisticRegression)
    assert model_path.is_file()

    bundle = joblib.dump.__globals__.get("joblib", joblib).load(model_path)
    assert "model" in bundle
    assert "metadata" in bundle
    assert bundle["metadata"]["algorithm"] == "logistic_regression"
    assert bundle["metadata"]["n_train_samples"] == 4
