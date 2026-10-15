"""Data preprocessing and group-aware partitioning stage for Phase 1 MLOps pipeline.

Performs conservative text normalization, enforces Zero-Null integrity,
and generates leakage-safe train/val/test splits grouped strictly by question_id.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Sequence

# Ensure project root is in sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import numpy as np
import pandas as pd

from src.utils.config import compute_data_fingerprint, get_logger, load_params

logger = get_logger("src.data.preprocess")


def normalize_text_conservatively(text: str) -> str:
    """Cleans whitespace and Unicode spaces while preserving technical terms and punctuation.

    Avoids lowercasing acronyms, stripping code symbols, or destroying code constructs.

    Args:
        text: Raw text string.

    Returns:
        Conservatively normalized string.
    """
    if not isinstance(text, str):
        return ""
    # Normalize non-breaking spaces and exotic Unicode whitespace
    cleaned = text.replace("\u00a0", " ").replace("\u200b", "")
    # Normalize excessive interior whitespace and linebreaks into clean single spaces
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n\s*\n+", "\n", cleaned)
    return cleaned.strip()


def group_aware_split(
    df: pd.DataFrame,
    group_column: str = "question_id",
    test_size: float = 0.20,
    val_size: float = 0.10,
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Splits DataFrame into train, val, and test partitions grouped by question_id.

    Guarantees zero question leakage: all candidate responses belonging to a given
    question exist strictly in one partition.

    Args:
        df: Input DataFrame.
        group_column: Column name containing group IDs (default 'question_id').
        test_size: Proportion of unique groups for test set (e.g. 0.20).
        val_size: Proportion of unique groups for validation set (e.g. 0.10).
        random_state: Seed for reproducible random group shuffling.

    Returns:
        Tuple of (train_df, val_df, test_df).

    Raises:
        ValueError: If group_column is missing, split ratios are invalid, or there
            are insufficient groups to create non-empty partitions.
    """
    if group_column not in df.columns:
        raise ValueError(
            f"Group column '{group_column}' not found in DataFrame. Available: {list(df.columns)}."
        )

    unique_groups: list[str] = sorted(df[group_column].unique().tolist())
    n_groups = len(unique_groups)

    if n_groups < 3:
        raise ValueError(
            f"Dataset has only {n_groups} unique '{group_column}' group(s). "
            "At least 3 distinct question groups are required to create non-empty "
            "train, validation, and test splits."
        )

    if test_size <= 0.0 or val_size < 0.0 or (test_size + val_size) >= 1.0:
        raise ValueError(
            f"Invalid split proportions (test_size={test_size}, val_size={val_size}). "
            "Proportions must be positive and their sum strictly less than 1.0."
        )

    # Deterministic shuffling of question groups
    rng = np.random.default_rng(random_state)
    shuffled_groups = rng.permutation(unique_groups).tolist()

    n_test = max(1, int(round(n_groups * test_size)))
    n_val = max(1, int(round(n_groups * val_size)))

    # Ensure train partition retains at least 1 group
    if n_test + n_val >= n_groups:
        n_test = 1
        n_val = 1

    test_groups: set[str] = set(shuffled_groups[:n_test])
    val_groups: set[str] = set(shuffled_groups[n_test : n_test + n_val])
    train_groups: set[str] = set(shuffled_groups[n_test + n_val :])

    # Defensive check: zero overlap across sets
    assert len(train_groups & val_groups) == 0, "Train and Val groups overlap!"
    assert len(train_groups & test_groups) == 0, "Train and Test groups overlap!"
    assert len(val_groups & test_groups) == 0, "Val and Test groups overlap!"

    train_df = df[df[group_column].isin(train_groups)].copy().reset_index(drop=True)
    val_df = df[df[group_column].isin(val_groups)].copy().reset_index(drop=True)
    test_df = df[df[group_column].isin(test_groups)].copy().reset_index(drop=True)

    if train_df.empty or val_df.empty or test_df.empty:
        raise ValueError(
            f"Split produced an empty partition: train={len(train_df)}, "
            f"val={len(val_df)}, test={len(test_df)} rows."
        )

    logger.info(
        f"Group-aware split complete: {n_groups} total questions -> "
        f"Train: {len(train_groups)} questions ({len(train_df)} rows), "
        f"Val: {len(val_groups)} questions ({len(val_df)} rows), "
        f"Test: {len(test_groups)} questions ({len(test_df)} rows)."
    )

    return train_df, val_df, test_df


def preprocess_data(
    input_path: str | Path,
    output_dir: str | Path,
    test_size: float = 0.20,
    val_size: float = 0.10,
    random_state: int = 42,
    text_columns: Sequence[str] = ("question", "candidate_answer", "reference_answer"),
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Loads interim Parquet, cleans text, and writes reproducible processed splits.

    Args:
        input_path: Path to interim loaded Parquet file.
        output_dir: Directory where train.parquet, val.parquet, test.parquet are written.
        test_size: Proportion of question groups for test split.
        val_size: Proportion of question groups for validation split.
        random_state: Random state for deterministic splitting.
        text_columns: List of columns to apply conservative normalization to.

    Returns:
        Tuple of (train_df, val_df, test_df).

    Raises:
        FileNotFoundError: If input interim Parquet does not exist.
    """
    in_file = Path(input_path)
    out_dir = Path(output_dir)

    if not in_file.is_file():
        raise FileNotFoundError(
            f"Input dataset not found at '{in_file.resolve()}'. "
            "Execute the ingestion or load_data stage first."
        )

    logger.info(f"Loading dataset from '{in_file}'...")
    if in_file.suffix == ".csv":
        df = pd.read_csv(in_file)
    else:
        df = pd.read_parquet(in_file)
    logger.info(f"Loaded {len(df)} rows.")

    # Conservative normalization of text fields
    for col in text_columns:
        if col in df.columns:
            logger.info(f"Conservatively normalizing text column '{col}'...")
            df[col] = df[col].astype(str).apply(normalize_text_conservatively)

    # Group-aware train / validation / test partitioning
    grp_col = "group_id" if "group_id" in df.columns else "question_id"
    train_df, val_df, test_df = group_aware_split(
        df=df,
        group_column=grp_col,
        test_size=test_size,
        val_size=val_size,
        random_state=random_state,
    )

    # Save processed splits
    out_dir.mkdir(parents=True, exist_ok=True)
    train_path = out_dir / "train.parquet"
    val_path = out_dir / "val.parquet"
    test_path = out_dir / "test.parquet"

    train_df.to_parquet(train_path, index=False)
    val_df.to_parquet(val_path, index=False)
    test_df.to_parquet(test_path, index=False)

    logger.info(
        f"Saved processed partitions to '{out_dir}':\n"
        f"  - Train: {train_path} ({len(train_df)} rows, SHA256: {compute_data_fingerprint(train_df)[:10]})\n"
        f"  - Val:   {val_path} ({len(val_df)} rows, SHA256: {compute_data_fingerprint(val_df)[:10]})\n"
        f"  - Test:  {test_path} ({len(test_df)} rows, SHA256: {compute_data_fingerprint(test_df)[:10]})"
    )

    return train_df, val_df, test_df


def main() -> None:
    """CLI entrypoint for DVC preprocess stage."""
    parser = argparse.ArgumentParser(description="Preprocess and split dataset by question groups.")
    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="Path to input dataset file (CSV or Parquet).",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/processed",
        help="Directory to save train, val, and test splits.",
    )
    args = parser.parse_args()

    params = load_params()
    raw_path = params.get("data", {}).get("raw_data_path", "data/raw/question_bank.csv")
    input_path = args.input or (
        raw_path if Path(raw_path).exists() else "data/interim/loaded_data.parquet"
    )

    split_cfg = params.get("split", {})
    test_size = float(split_cfg.get("test_size", 0.20))
    val_size = float(split_cfg.get("validation_size", 0.10))
    random_state = int(split_cfg.get("random_state", 42))

    preprocess_data(
        input_path=input_path,
        output_dir=args.output_dir,
        test_size=test_size,
        val_size=val_size,
        random_state=random_state,
    )


if __name__ == "__main__":
    main()
