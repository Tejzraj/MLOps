"""Unit tests for data loading, preprocessing, and group leakage prevention.

Tests use temporary in-memory CSV/Parquet files created dynamically with pytest's tmp_path.
No external or real interview data is used.
"""

from __future__ import annotations

import pandas as pd
import pytest

from src.data.load_data import load_and_validate_data
from src.data.preprocess import (
    group_aware_split,
    normalize_text_conservatively,
    preprocess_data,
)


@pytest.fixture
def sample_raw_dataframe() -> pd.DataFrame:
    """Creates a minimal valid DataFrame with multiple question groups."""
    rows = []
    # Create 4 distinct questions to allow valid train, val, and test partitions
    for q_idx in range(1, 5):
        qid = f"Q_OS_{q_idx:03d}"
        for c_idx, label in enumerate([0, 1, 2, 3]):
            score = label * 4  # 0, 4, 8, 12
            rows.append(
                {
                    "question_id": qid,
                    "domain": "Operating Systems",
                    "difficulty": "Medium",
                    "question_type": "Comparative",
                    "question": f"Question prompt text for {qid}?",
                    "reference_answer": f"Expert reference answer for {qid}.",
                    "expected_concepts": "concept1; concept2; concept3",
                    "candidate_answer": f"Candidate answer variant {c_idx} for {qid}.",
                    "correctness_score": min(5, score // 3),
                    "completeness_score": min(5, score // 3),
                    "communication_score": min(5, score - 2 * (score // 3)),
                    "total_score": score,
                    "quality_label": label,
                    "source": "curriculum_standard",
                    "source_license": "Apache-2.0",
                    "annotator_id": "ANN_01",
                    "annotation_method": "human_rubric_adjudicated",
                    "version": "v0.1.0",
                    "split_group": qid,
                }
            )
    return pd.DataFrame(rows)


def test_load_data_file_not_found(tmp_path: pytest.TempPathFactory) -> None:
    """Verifies that load_and_validate_data raises FileNotFoundError when input is missing."""
    missing_file = tmp_path / "nonexistent.csv"
    output_file = tmp_path / "out.parquet"

    with pytest.raises(FileNotFoundError, match="Raw dataset not found"):
        load_and_validate_data(missing_file, output_file)


def test_load_data_success_and_alias(
    tmp_path: pytest.TempPathFactory, sample_raw_dataframe: pd.DataFrame
) -> None:
    """Verifies successful loading, aliasing of interview_question, and interim write."""
    df_with_alias = sample_raw_dataframe.rename(columns={"question": "interview_question"})
    input_csv = tmp_path / "raw.csv"
    output_parquet = tmp_path / "interim.parquet"

    df_with_alias.to_csv(input_csv, index=False)
    loaded_df = load_and_validate_data(input_csv, output_parquet)

    assert output_parquet.is_file()
    assert "question" in loaded_df.columns
    assert len(loaded_df) == len(sample_raw_dataframe)


def test_text_normalization_conservative() -> None:
    """Verifies conservative text cleaning preserves technical terms and punctuation."""
    raw = "  Explain   C/C++  threads  vs  processes! \u00a0\n\nPointer: *ptr == NULL;  "
    cleaned = normalize_text_conservatively(raw)

    assert "C/C++" in cleaned
    assert "*ptr == NULL;" in cleaned
    assert "  " not in cleaned
    assert cleaned.startswith("Explain")


def test_group_aware_split_no_leakage(sample_raw_dataframe: pd.DataFrame) -> None:
    """Verifies that no question_id appears in more than one partition."""
    train_df, val_df, test_df = group_aware_split(
        df=sample_raw_dataframe,
        group_column="question_id",
        test_size=0.25,
        val_size=0.25,
        random_state=42,
    )

    train_q = set(train_df["question_id"])
    val_q = set(val_df["question_id"])
    test_q = set(test_df["question_id"])

    # Strict leakage assertion: disjoint question sets
    assert len(train_q & val_q) == 0, f"Train and Val share questions: {train_q & val_q}"
    assert len(train_q & test_q) == 0, f"Train and Test share questions: {train_q & test_q}"
    assert len(val_q & test_q) == 0, f"Val and Test share questions: {val_q & test_q}"

    # Non-empty partitions
    assert len(train_df) > 0
    assert len(val_df) > 0
    assert len(test_df) > 0
    assert len(train_df) + len(val_df) + len(test_df) == len(sample_raw_dataframe)


def test_group_aware_split_insufficient_groups(sample_raw_dataframe: pd.DataFrame) -> None:
    """Verifies that having fewer than 3 unique questions raises ValueError."""
    # Filter to only 2 questions
    tiny_df = sample_raw_dataframe[
        sample_raw_dataframe["question_id"].isin(["Q_OS_001", "Q_OS_002"])
    ]

    with pytest.raises(ValueError, match="At least 3 distinct question groups"):
        group_aware_split(tiny_df, group_column="question_id")


def test_preprocess_data_end_to_end(
    tmp_path: pytest.TempPathFactory, sample_raw_dataframe: pd.DataFrame
) -> None:
    """Verifies preprocess_data reads interim Parquet and outputs all three processed splits."""
    interim_path = tmp_path / "interim.parquet"
    out_dir = tmp_path / "processed"

    sample_raw_dataframe.to_parquet(interim_path, index=False)
    train_df, val_df, test_df = preprocess_data(
        input_path=interim_path,
        output_dir=out_dir,
        test_size=0.25,
        val_size=0.25,
        random_state=42,
    )

    assert (out_dir / "train.parquet").is_file()
    assert (out_dir / "val.parquet").is_file()
    assert (out_dir / "test.parquet").is_file()
    assert len(train_df) > 0
    assert len(val_df) > 0
    assert len(test_df) > 0
