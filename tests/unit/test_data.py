"""Unit tests for dataset schema validation module.

Validates that in-memory pandas DataFrames conform strictly to the 19-field
schema and proposed pedagogical rubrics documented in docs/dataset/.

Note: Tests use exclusively in-memory synthetic DataFrames; no external data
is downloaded, modified, or saved to disk.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import pytest

from src.data.validation import (
    DatasetValidationError,
    map_score_to_proposed_label,
    validate_dataset,
)


@pytest.fixture
def valid_row_dict() -> dict[str, Any]:
    """Provides a single valid record conforming to the documented 19-field schema."""
    return {
        "question_id": "Q_OS_001",
        "domain": "Operating Systems",
        "difficulty": "Medium",
        "question_type": "Comparative",
        "question": "Explain the difference between a process and a thread.",
        "reference_answer": "A process has isolated virtual address space, threads share process memory.",
        "expected_concepts": "isolated memory; shared memory; context switch overhead",
        "candidate_answer": "A process is an execution unit with its own memory, while threads share memory.",
        "correctness_score": 4,
        "completeness_score": 4,
        "communication_score": 3,
        "total_score": 11,
        "quality_label": 2,  # Good (Proposed 8-11)
        "source": "curriculum_standard",
        "source_license": "Apache-2.0",
        "annotator_id": "ANN_01",
        "annotation_method": "human_rubric_adjudicated",
        "version": "v0.1.0",
        "split_group": "Q_OS_001",
    }


def test_valid_dataframe_single_row(valid_row_dict: dict[str, Any]) -> None:
    """Verifies that a compliant single-row DataFrame passes validation."""
    df = pd.DataFrame([valid_row_dict])
    result = validate_dataset(df)
    assert result.is_valid, f"Expected valid, got errors: {result.errors}"
    assert len(result.errors) == 0


def test_valid_dataframe_all_four_tiers(valid_row_dict: dict[str, Any]) -> None:
    """Verifies that valid responses across all four proposed tiers pass."""
    rows = []
    # Tier 0: Poor (total: 2, label: 0)
    r0 = valid_row_dict.copy()
    r0.update(
        {
            "question_id": "Q_OS_001",
            "candidate_answer": "Threads are faster things.",
            "correctness_score": 1,
            "completeness_score": 1,
            "communication_score": 0,
            "total_score": 2,
            "quality_label": 0,
            "split_group": "Q_OS_001",
        }
    )
    rows.append(r0)

    # Tier 1: Needs Improvement (total: 5, label: 1)
    r1 = valid_row_dict.copy()
    r1.update(
        {
            "question_id": "Q_OS_001",
            "candidate_answer": "A process has memory. Threads are inside processes and run faster.",
            "correctness_score": 2,
            "completeness_score": 2,
            "communication_score": 1,
            "total_score": 5,
            "quality_label": 1,
            "split_group": "Q_OS_001",
        }
    )
    rows.append(r1)

    # Tier 2: Good (total: 10, label: 2)
    r2 = valid_row_dict.copy()
    r2.update(
        {
            "question_id": "Q_OS_001",
            "candidate_answer": "Processes possess separate memory spaces, threads share parent process memory.",
            "correctness_score": 4,
            "completeness_score": 3,
            "communication_score": 3,
            "total_score": 10,
            "quality_label": 2,
            "split_group": "Q_OS_001",
        }
    )
    rows.append(r2)

    # Tier 3: Excellent (total: 14, label: 3)
    r3 = valid_row_dict.copy()
    r3.update(
        {
            "question_id": "Q_OS_001",
            "candidate_answer": "A process represents an independent executing program with isolated address space and file descriptors. Threads are lightweight execution units within a process sharing memory.",
            "correctness_score": 5,
            "completeness_score": 5,
            "communication_score": 4,
            "total_score": 14,
            "quality_label": 3,
            "split_group": "Q_OS_001",
        }
    )
    rows.append(r3)

    df = pd.DataFrame(rows)
    result = validate_dataset(df)
    assert result.is_valid, f"Validation failed: {result.errors}"


def test_valid_domain_acronyms_accepted(valid_row_dict: dict[str, Any]) -> None:
    """Verifies that recognized domain acronyms (e.g. OS, DSA, ML) are accepted."""
    df = pd.DataFrame(
        [
            {**valid_row_dict, "domain": "OS"},
            {
                **valid_row_dict,
                "question_id": "Q_ML_002",
                "split_group": "Q_ML_002",
                "domain": "ML",
            },
        ]
    )
    result = validate_dataset(df)
    assert result.is_valid, f"Expected valid acronyms, got: {result.errors}"


def test_valid_behavioral_hr_question_type(valid_row_dict: dict[str, Any]) -> None:
    """Verifies Behavioral / HR is accepted as question_type without creating an invalid domain."""
    row = valid_row_dict.copy()
    row["question_type"] = "Behavioral / HR"
    row["domain"] = "Python"
    df = pd.DataFrame([row])
    result = validate_dataset(df)
    assert result.is_valid, f"Expected valid question_type, got: {result.errors}"


def test_missing_column_rejected(valid_row_dict: dict[str, Any]) -> None:
    """Verifies that dropping a required schema column fails validation."""
    df = pd.DataFrame([valid_row_dict]).drop(columns=["quality_label"])
    result = validate_dataset(df)
    assert not result.is_valid
    assert any("quality_label" in err for err in result.errors)


def test_unexpected_columns_rejected_by_default(valid_row_dict: dict[str, Any]) -> None:
    """Verifies that adding an unexpected column fails under strict contract."""
    row = valid_row_dict.copy()
    row["extra_unapproved_column"] = "some_value"
    df = pd.DataFrame([row])
    result = validate_dataset(df)
    assert not result.is_valid
    assert any("extra_unapproved_column" in err for err in result.errors)


def test_unexpected_columns_permitted_when_configured(valid_row_dict: dict[str, Any]) -> None:
    """Verifies that extra columns pass when allow_extra_columns=True."""
    row = valid_row_dict.copy()
    row["extra_info"] = "debug_flag"
    df = pd.DataFrame([row])
    result = validate_dataset(df, allow_extra_columns=True)
    assert result.is_valid


def test_empty_dataframe_rejected() -> None:
    """Verifies that an empty DataFrame fails validation."""
    df = pd.DataFrame()
    result = validate_dataset(df)
    assert not result.is_valid
    assert any("empty" in err.lower() for err in result.errors)


def test_non_dataframe_input_rejected() -> None:
    """Verifies that non-DataFrame input returns an invalid result."""
    result = validate_dataset([{"some": "dict"}])
    assert not result.is_valid
    assert any("pandas DataFrame" in err for err in result.errors)


def test_invalid_domain_rejected(valid_row_dict: dict[str, Any]) -> None:
    """Verifies that unapproved domain names are rejected."""
    row = valid_row_dict.copy()
    row["domain"] = "Biology"
    df = pd.DataFrame([row])
    result = validate_dataset(df)
    assert not result.is_valid
    assert any("Invalid domain" in err for err in result.errors)


def test_behavioral_as_domain_rejected(valid_row_dict: dict[str, Any]) -> None:
    """Verifies that 'Behavioral' is rejected as a domain (it belongs under question_type)."""
    row = valid_row_dict.copy()
    row["domain"] = "Behavioral"
    df = pd.DataFrame([row])
    result = validate_dataset(df)
    assert not result.is_valid
    assert any("Invalid domain" in err for err in result.errors)


def test_invalid_difficulty_rejected(valid_row_dict: dict[str, Any]) -> None:
    """Verifies that invalid difficulty tiers are rejected."""
    row = valid_row_dict.copy()
    row["difficulty"] = "Extreme"
    df = pd.DataFrame([row])
    result = validate_dataset(df)
    assert not result.is_valid
    assert any("Invalid difficulty" in err for err in result.errors)


def test_invalid_question_type_rejected(valid_row_dict: dict[str, Any]) -> None:
    """Verifies that invalid question types are rejected."""
    row = valid_row_dict.copy()
    row["question_type"] = "Multiple Choice"
    df = pd.DataFrame([row])
    result = validate_dataset(df)
    assert not result.is_valid
    assert any("Invalid question_type" in err for err in result.errors)


def test_invalid_quality_label_rejected(valid_row_dict: dict[str, Any]) -> None:
    """Verifies that quality labels outside {0, 1, 2, 3} are rejected."""
    row = valid_row_dict.copy()
    row["quality_label"] = 4  # Beyond 0-3
    df = pd.DataFrame([row])
    result = validate_dataset(df)
    assert not result.is_valid
    assert any("Invalid quality_label" in err for err in result.errors)


def test_missing_or_null_values_rejected(valid_row_dict: dict[str, Any]) -> None:
    """Verifies that null / NaN values violate the zero-null policy."""
    row = valid_row_dict.copy()
    row["candidate_answer"] = None
    df = pd.DataFrame([row])
    result = validate_dataset(df)
    assert not result.is_valid
    assert any("Zero-Null Policy" in err for err in result.errors)


def test_blank_whitespace_text_rejected(valid_row_dict: dict[str, Any]) -> None:
    """Verifies that blank or whitespace-only text entries are rejected."""
    row = valid_row_dict.copy()
    row["candidate_answer"] = "    "
    df = pd.DataFrame([row])
    result = validate_dataset(df)
    assert not result.is_valid
    assert any("blank or whitespace-only" in err for err in result.errors)


def test_component_score_out_of_range_rejected(valid_row_dict: dict[str, Any]) -> None:
    """Verifies component scores outside [0, 5] fail."""
    row = valid_row_dict.copy()
    row["correctness_score"] = 6
    df = pd.DataFrame([row])
    result = validate_dataset(df)
    assert not result.is_valid
    assert any("outside allowed range [0, 5]" in err for err in result.errors)


def test_negative_component_score_rejected(valid_row_dict: dict[str, Any]) -> None:
    """Verifies negative component scores fail."""
    row = valid_row_dict.copy()
    row["completeness_score"] = -1
    df = pd.DataFrame([row])
    result = validate_dataset(df)
    assert not result.is_valid
    assert any("outside allowed range [0, 5]" in err for err in result.errors)


def test_total_score_sum_inconsistency_rejected(valid_row_dict: dict[str, Any]) -> None:
    """Verifies that total_score != sum(component_scores) fails."""
    row = valid_row_dict.copy()
    # Correctness(4) + Completeness(4) + Communication(3) = 11, set total to 10
    row["total_score"] = 10
    df = pd.DataFrame([row])
    result = validate_dataset(df)
    assert not result.is_valid
    assert any("inconsistent with sum of components" in err for err in result.errors)


def test_proposed_label_mismatch_rejected(valid_row_dict: dict[str, Any]) -> None:
    """Verifies that quality_label deviating from the proposed total_score mapping fails."""
    row = valid_row_dict.copy()
    # total_score 11 maps to proposed label 2 (Good), set label to 0 (Poor)
    row["correctness_score"] = 4
    row["completeness_score"] = 4
    row["communication_score"] = 3
    row["total_score"] = 11
    row["quality_label"] = 0
    df = pd.DataFrame([row])
    result = validate_dataset(df)
    assert not result.is_valid
    assert any("Proposed quality label mismatch" in err for err in result.errors)


def test_proposed_label_check_can_be_disabled(valid_row_dict: dict[str, Any]) -> None:
    """Verifies check_proposed_thresholds=False allows atypical labels if calibrated differently."""
    row = valid_row_dict.copy()
    row["total_score"] = 11
    row["quality_label"] = 1  # Divergent from proposed mapping
    df = pd.DataFrame([row])
    result = validate_dataset(df, check_proposed_thresholds=False)
    assert result.is_valid


def test_split_group_mismatch_rejected(valid_row_dict: dict[str, Any]) -> None:
    """Verifies that split_group != question_id is flagged to prevent leakage."""
    row = valid_row_dict.copy()
    row["split_group"] = "DIFFERENT_ID_009"
    df = pd.DataFrame([row])
    result = validate_dataset(df)
    assert not result.is_valid
    assert any("Split group mismatch" in err for err in result.errors)


def test_duplicate_candidate_response_rejected(valid_row_dict: dict[str, Any]) -> None:
    """Verifies that duplicate (question_id, candidate_answer) pairs fail."""
    df = pd.DataFrame([valid_row_dict, valid_row_dict])
    result = validate_dataset(df)
    assert not result.is_valid
    assert any("Duplicate candidate response" in err for err in result.errors)


def test_raise_on_error_raises_dataset_validation_error(valid_row_dict: dict[str, Any]) -> None:
    """Verifies that raise_on_error=True raises DatasetValidationError with descriptive message."""
    row = valid_row_dict.copy()
    row["difficulty"] = "InvalidLevel"
    df = pd.DataFrame([row])
    with pytest.raises(DatasetValidationError) as exc_info:
        validate_dataset(df, raise_on_error=True)
    assert "Dataset validation failed" in str(exc_info.value)
    assert len(exc_info.value.errors) > 0


def test_map_score_to_proposed_label_boundaries() -> None:
    """Verifies map_score_to_proposed_label boundary conditions and error handling."""
    # Proposed boundaries: 0-3 -> 0, 4-7 -> 1, 8-11 -> 2, 12-15 -> 3
    assert map_score_to_proposed_label(0) == 0
    assert map_score_to_proposed_label(3) == 0
    assert map_score_to_proposed_label(4) == 1
    assert map_score_to_proposed_label(7) == 1
    assert map_score_to_proposed_label(8) == 2
    assert map_score_to_proposed_label(11) == 2
    assert map_score_to_proposed_label(12) == 3
    assert map_score_to_proposed_label(15) == 3

    with pytest.raises(ValueError, match="outside allowed range"):
        map_score_to_proposed_label(-1)

    with pytest.raises(ValueError, match="outside allowed range"):
        map_score_to_proposed_label(16)
