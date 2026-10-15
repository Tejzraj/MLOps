"""Feature engineering stage for Phase 1 MLOps pipeline.

Extracts text features using TF-IDF vectorization. Fits exclusively on
training partition to prevent test leakage and serializes the fitted
vectorizer for inference and evaluation.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Sequence

# Ensure project root is in sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import joblib
import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer

from src.utils.config import get_logger, load_params

logger = get_logger("src.features.build_features")

# Explicit definition of input columns used for model training.
# All score columns, target labels, and metadata are strictly excluded
# to prevent target leakage.
FEATURE_INPUT_COLUMNS: list[str] = ["question", "candidate_answer"]
TARGET_COLUMN: str = "quality_label"


def prepare_text_corpus(df: pd.DataFrame, text_columns: Sequence[str] | None = None) -> list[str]:
    """Combines configured text columns into a clean text representation.

    Supports both domain classification (where only 'question' is available)
    and candidate-answer quality grading (where 'question' and 'candidate_answer' are combined).

    Args:
        df: Input DataFrame.
        text_columns: Optional sequence of text columns to use.

    Returns:
        List of concatenated text strings for TF-IDF feature extraction.

    Raises:
        ValueError: If required text columns are missing.
    """
    if text_columns is not None:
        cols = [c for c in text_columns if c]
    elif "domain" in df.columns and "candidate_answer" not in df.columns:
        cols = ["question"]
    else:
        cols = FEATURE_INPUT_COLUMNS

    for col in cols:
        if col not in df.columns:
            raise ValueError(
                f"Required input feature column '{col}' missing from DataFrame. "
                f"Available: {list(df.columns)}."
            )

    if len(cols) == 1:
        return df[cols[0]].astype(str).str.strip().tolist()

    combined = df[cols[0]].astype(str).str.strip() + " [SEP] " + df[cols[1]].astype(str).str.strip()
    return combined.tolist()


def create_vectorizer(tfidf_params: dict[str, Any] | None = None) -> TfidfVectorizer:
    """Instantiates a scikit-learn TfidfVectorizer with configured parameters.

    Args:
        tfidf_params: Dictionary of TF-IDF hyperparameters from params.yaml.

    Returns:
        Configured TfidfVectorizer instance.
    """
    params = tfidf_params or {}

    max_features = params.get("max_features", 5000)
    ngram_range_raw = params.get("ngram_range", [1, 2])
    ngram_range = tuple(ngram_range_raw) if isinstance(ngram_range_raw, list) else ngram_range_raw
    stop_words = params.get("stop_words", "english")
    min_df = params.get("min_df", 2)
    sublinear_tf = params.get("sublinear_tf", True)

    logger.info(
        f"Configuring TfidfVectorizer: max_features={max_features}, "
        f"ngram_range={ngram_range}, stop_words={stop_words}, "
        f"min_df={min_df}, sublinear_tf={sublinear_tf}"
    )

    return TfidfVectorizer(
        max_features=max_features,
        ngram_range=ngram_range,
        stop_words=stop_words,
        min_df=min_df,
        sublinear_tf=sublinear_tf,
    )


def fit_feature_pipeline(
    train_df: pd.DataFrame,
    tfidf_params: dict[str, Any] | None = None,
    text_columns: Sequence[str] | None = None,
) -> TfidfVectorizer:
    """Fits TF-IDF vectorizer on training data exclusively to prevent leakage.

    Args:
        train_df: Training DataFrame containing text columns.
        tfidf_params: Hyperparameter dictionary for TF-IDF.
        text_columns: Optional sequence of text columns.

    Returns:
        Fitted TfidfVectorizer.

    Raises:
        ValueError: If train_df is empty.
    """
    if train_df.empty:
        raise ValueError("Cannot fit feature pipeline on empty training DataFrame.")

    corpus = prepare_text_corpus(train_df, text_columns=text_columns)
    vectorizer = create_vectorizer(tfidf_params)

    # For tiny datasets in tests, min_df=2 might fail if terms occur only once
    if len(train_df) < 5 and vectorizer.min_df > 1:
        logger.warning(
            f"Training set has only {len(train_df)} rows. Adjusting min_df from {vectorizer.min_df} to 1."
        )
        vectorizer.min_df = 1

    logger.info(f"Fitting TF-IDF vectorizer on {len(corpus)} training samples...")
    vectorizer.fit(corpus)
    logger.info(f"Vectorizer fitted successfully. Vocabulary size: {len(vectorizer.vocabulary_)}.")

    return vectorizer


def transform_features(
    df: pd.DataFrame,
    vectorizer: TfidfVectorizer,
    target_column: str | None = None,
    text_columns: Sequence[str] | None = None,
) -> tuple[sparse.csr_matrix, np.ndarray | None]:
    """Transforms a DataFrame using a fitted vectorizer and extracts labels if present.

    Args:
        df: Input DataFrame.
        vectorizer: Fitted TfidfVectorizer.
        target_column: Optional target column name to extract (defaults to TARGET_COLUMN or 'domain').
        text_columns: Optional text columns to use.

    Returns:
        Tuple of (feature_matrix_X, target_labels_y_or_None).
    """
    corpus = prepare_text_corpus(df, text_columns=text_columns)
    x_matrix = vectorizer.transform(corpus)

    y_labels: np.ndarray | None = None
    target_col = target_column
    if target_col is None:
        target_col = "domain" if "domain" in df.columns else TARGET_COLUMN

    if target_col in df.columns:
        y_labels = df[target_col].to_numpy()

    return x_matrix, y_labels


def build_features(
    train_path: str | Path,
    output_model_path: str | Path,
    tfidf_params: dict[str, Any] | None = None,
) -> TfidfVectorizer:
    """Pipeline entrypoint: loads train data, fits vectorizer, and serializes artifact.

    Args:
        train_path: Path to processed train.parquet.
        output_model_path: Path to save models/tfidf_vectorizer.joblib.
        tfidf_params: Optional TF-IDF parameters.

    Returns:
        Fitted TfidfVectorizer.

    Raises:
        FileNotFoundError: If train_path does not exist.
    """
    train_file = Path(train_path)
    out_file = Path(output_model_path)

    if not train_file.is_file():
        raise FileNotFoundError(
            f"Processed training set not found at '{train_file.resolve()}'. "
            "Please run the preprocess stage first."
        )

    logger.info(f"Loading training data from '{train_file}'...")
    train_df = pd.read_parquet(train_file)
    logger.info(f"Loaded {len(train_df)} training samples.")

    vectorizer = fit_feature_pipeline(train_df, tfidf_params=tfidf_params)

    out_file.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(vectorizer, out_file)
    logger.info(f"Saved fitted TF-IDF vectorizer artifact to '{out_file}'.")

    return vectorizer


def main() -> None:
    """CLI entrypoint for DVC feature_engineering stage."""
    parser = argparse.ArgumentParser(description="Fit TF-IDF feature pipeline on train data.")
    parser.add_argument(
        "--train-data",
        type=str,
        default="data/processed/train.parquet",
        help="Path to training Parquet split.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="models/tfidf_vectorizer.joblib",
        help="Path to save fitted vectorizer artifact.",
    )
    args = parser.parse_args()

    params = load_params()
    tfidf_params = params.get("features", {}).get("tfidf", {})

    build_features(
        train_path=args.train_data,
        output_model_path=args.output,
        tfidf_params=tfidf_params,
    )


if __name__ == "__main__":
    main()
