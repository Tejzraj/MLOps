"""Dataset schema validation module for AI-Based Interview Preparation Assistant.

Validates in-memory pandas DataFrames against the 19-field dataset schema
defined in docs/dataset/DATASET_SPECIFICATION.md, docs/dataset/LABELING_GUIDELINES.md,
and docs/dataset/DATA_COLLECTION.md.

Note on Quality Thresholds:
The score-to-label boundaries (0-3 Poor, 4-7 Needs Improvement, 8-11 Good, 12-15 Excellent)
represent a PROPOSED rubric mapping that is SUBJECT TO FACULTY VALIDATION AND ANNOTATION
CALIBRATION. They are not scientifically validated constants or established ground truth.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

import pandas as pd

# ==============================================================================
# Documented 19-Field Dataset Schema
# Source: docs/dataset/DATASET_SPECIFICATION.md (Section 10)
# ==============================================================================
SCHEMA_COLUMNS: list[str] = [
    "question_id",
    "domain",
    "difficulty",
    "question_type",
    "question",
    "reference_answer",
    "expected_concepts",
    "candidate_answer",
    "correctness_score",
    "completeness_score",
    "communication_score",
    "total_score",
    "quality_label",
    "source",
    "source_license",
    "annotator_id",
    "annotation_method",
    "version",
    "split_group",
]

# 10 Approved Technical Computer Science & AI Domains
# Source: docs/dataset/DATASET_SPECIFICATION.md (Section 7), DATA_COLLECTION.md (Stage 4)
# Note: Behavioral / HR questions are classified under question_type, NOT as a technical domain.
CANONICAL_DOMAINS: set[str] = {
    "Data Structures & Algorithms",
    "Object-Oriented Programming",
    "Database Management Systems",
    "Computer Networks",
    "Operating Systems",
    "Python",
    "C/C++",
    "Java",
    "Machine Learning",
    "Artificial Intelligence",
}

# Standard domain acronyms recognized in project documentation
DOMAIN_ACRONYMS: set[str] = {
    "DSA",
    "OOP",
    "DBMS",
    "CN",
    "OS",
    "ML",
    "AI",
}

ALLOWED_DOMAINS: set[str] = CANONICAL_DOMAINS | DOMAIN_ACRONYMS

# Difficulty tiers
# Source: docs/dataset/DATASET_SPECIFICATION.md (Section 8)
ALLOWED_DIFFICULTIES: set[str] = {
    "Easy",
    "Medium",
    "Hard",
}

# Question types
# Source: docs/dataset/DATASET_SPECIFICATION.md (Section 9 & 10)
ALLOWED_QUESTION_TYPES: set[str] = {
    "Conceptual",
    "Comparative",
    "Diagnostic",
    "Behavioral / HR",
    "Behavioral/HR",  # Tolerant format without spaces
}

# Quality labels (4-tier ordinal classification)
# Source: docs/dataset/DATASET_SPECIFICATION.md (Section 11)
ALLOWED_QUALITY_LABELS: set[int] = {0, 1, 2, 3}

# Component score ranges (0 to 5)
COMPONENT_SCORE_MIN: int = 0
COMPONENT_SCORE_MAX: int = 5

# Composite score range (0 to 15)
TOTAL_SCORE_MIN: int = 0
TOTAL_SCORE_MAX: int = 15

# Proposed quality label intervals
# PROPOSED — SUBJECT TO FACULTY VALIDATION AND ANNOTATION CALIBRATION
PROPOSED_LABEL_MAPPING: dict[int, tuple[int, int]] = {
    0: (0, 3),  # Poor
    1: (4, 7),  # Needs Improvement
    2: (8, 11),  # Good
    3: (12, 15),  # Excellent
}

PROPOSED_LABEL_NAMES: dict[int, str] = {
    0: "Poor",
    1: "Needs Improvement",
    2: "Good",
    3: "Excellent",
}

TEXT_COLUMNS: Sequence[str] = (
    "question_id",
    "domain",
    "difficulty",
    "question_type",
    "question",
    "reference_answer",
    "expected_concepts",
    "candidate_answer",
    "source",
    "source_license",
    "annotator_id",
    "annotation_method",
    "version",
    "split_group",
)

COMPONENT_SCORE_COLUMNS: Sequence[str] = (
    "correctness_score",
    "completeness_score",
    "communication_score",
)


class DatasetValidationError(ValueError):
    """Exception raised when dataset schema or value validation fails."""

    def __init__(self, message: str, errors: list[str] | None = None) -> None:
        super().__init__(message)
        self.errors: list[str] = errors or []


@dataclass
class ValidationResult:
    """Encapsulates validation outcome, errors, and warnings.

    Attributes:
        is_valid: True if no validation errors were found.
        errors: List of actionable error descriptions.
        warnings: List of advisory warnings or calibration notes.
    """

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def raise_if_invalid(self) -> None:
        """Raise DatasetValidationError if is_valid is False."""
        if not self.is_valid:
            summary = f"Dataset validation failed with {len(self.errors)} error(s):\n" + "\n".join(
                f"  - {err}" for err in self.errors
            )
            raise DatasetValidationError(summary, errors=self.errors)


def map_score_to_proposed_label(total_score: int) -> int:
    """Maps a composite total score (0-15) to its PROPOSED quality label (0-3).

    Note: This mapping reflects our proposed rubric working hypothesis
    (0-3 Poor, 4-7 Needs Improvement, 8-11 Good, 12-15 Excellent) and is
    SUBJECT TO FACULTY VALIDATION AND ANNOTATION CALIBRATION.

    Args:
        total_score: Sum of correctness, completeness, and communication scores.

    Returns:
        Proposed class label (0, 1, 2, or 3).

    Raises:
        ValueError: If total_score is outside [0, 15].
    """
    if not (TOTAL_SCORE_MIN <= total_score <= TOTAL_SCORE_MAX):
        raise ValueError(
            f"Total score {total_score} outside allowed range [{TOTAL_SCORE_MIN}, {TOTAL_SCORE_MAX}]."
        )
    for label, (low, high) in PROPOSED_LABEL_MAPPING.items():
        if low <= total_score <= high:
            return label
    raise ValueError(f"Unable to map total score {total_score} to proposed label.")


def _validate_columns(df: pd.DataFrame, allow_extra_columns: bool) -> tuple[list[str], bool]:
    """Checks for missing and unexpected columns. Returns (errors, has_missing)."""
    errors: list[str] = []
    existing_cols = list(df.columns)
    missing_cols = [c for c in SCHEMA_COLUMNS if c not in existing_cols]
    if missing_cols:
        errors.append(f"Missing required schema column(s): {missing_cols}.")

    if not allow_extra_columns:
        unexpected_cols = [c for c in existing_cols if c not in SCHEMA_COLUMNS]
        if unexpected_cols:
            errors.append(f"Unexpected column(s) not in schema: {unexpected_cols}.")

    return errors, len(missing_cols) > 0


def _validate_nulls_and_blanks(df: pd.DataFrame) -> list[str]:
    """Validates Zero-Null policy and rejects blank or whitespace-only strings."""
    errors: list[str] = []
    for col in SCHEMA_COLUMNS:
        null_mask = df[col].isna()
        if null_mask.any():
            bad_indices = df.index[null_mask].tolist()
            errors.append(
                f"Column '{col}' violates Zero-Null Policy: found {len(bad_indices)} "
                f"null/missing value(s) at row index(es) {bad_indices[:5]}."
            )

    for col in TEXT_COLUMNS:
        series = df[col].dropna()
        blank_mask = series.apply(lambda val: isinstance(val, str) and val.strip() == "")
        if blank_mask.any():
            bad_indices = df.index[blank_mask].tolist()
            errors.append(
                f"Column '{col}' has {len(bad_indices)} blank or whitespace-only value(s) "
                f"at row index(es) {bad_indices[:5]}."
            )
    return errors


def _validate_domain(df: pd.DataFrame) -> list[str]:
    """Validates domain values against the 10 approved domains and acronyms."""
    invalid = [
        (idx, val)
        for idx, val in df["domain"].dropna().items()
        if str(val).strip() not in ALLOWED_DOMAINS
    ]
    if not invalid:
        return []
    examples = [f"row {idx}: '{val}'" for idx, val in invalid[:5]]
    return [
        f"Invalid domain(s) found in {len(invalid)} row(s): {examples}. "
        f"Must be one of the 10 approved domains: {sorted(CANONICAL_DOMAINS)}."
    ]


def _validate_difficulty(df: pd.DataFrame) -> list[str]:
    """Validates difficulty values against allowed levels."""
    invalid = [
        (idx, val)
        for idx, val in df["difficulty"].dropna().items()
        if str(val).strip() not in ALLOWED_DIFFICULTIES
    ]
    if not invalid:
        return []
    examples = [f"row {idx}: '{val}'" for idx, val in invalid[:5]]
    return [
        f"Invalid difficulty level(s) found in {len(invalid)} row(s): {examples}. "
        f"Allowed values are: {sorted(ALLOWED_DIFFICULTIES)}."
    ]


def _validate_question_type(df: pd.DataFrame) -> list[str]:
    """Validates question_type values."""
    invalid = [
        (idx, val)
        for idx, val in df["question_type"].dropna().items()
        if str(val).strip() not in ALLOWED_QUESTION_TYPES
    ]
    if not invalid:
        return []
    examples = [f"row {idx}: '{val}'" for idx, val in invalid[:5]]
    return [
        f"Invalid question_type found in {len(invalid)} row(s): {examples}. "
        f"Allowed values are: {sorted(ALLOWED_QUESTION_TYPES)}."
    ]


def _validate_quality_label(df: pd.DataFrame) -> list[str]:
    """Validates quality_label integer values."""
    invalid: list[tuple[int, Any]] = []
    for idx, val in df["quality_label"].dropna().items():
        try:
            int_val = int(val)
            if int_val != val or int_val not in ALLOWED_QUALITY_LABELS:
                invalid.append((idx, val))
        except (ValueError, TypeError):
            invalid.append((idx, val))
    if not invalid:
        return []
    examples = [f"row {idx}: '{val}'" for idx, val in invalid[:5]]
    return [
        f"Invalid quality_label found in {len(invalid)} row(s): {examples}. "
        f"Must be integer in {sorted(ALLOWED_QUALITY_LABELS)}."
    ]


def _validate_taxonomy(df: pd.DataFrame) -> list[str]:
    """Aggregates taxonomy validations for domain, difficulty, question_type, and label."""
    errors: list[str] = []
    errors.extend(_validate_domain(df))
    errors.extend(_validate_difficulty(df))
    errors.extend(_validate_question_type(df))
    errors.extend(_validate_quality_label(df))
    return errors


def _validate_component_scores(df: pd.DataFrame) -> list[str]:
    """Validates component scores lie within [0, 5]."""
    errors: list[str] = []
    for col in COMPONENT_SCORE_COLUMNS:
        for idx, val in df[col].dropna().items():
            try:
                int_val = int(val)
                if int_val != val or not (COMPONENT_SCORE_MIN <= int_val <= COMPONENT_SCORE_MAX):
                    errors.append(
                        f"Row {idx}: '{col}' value {val} is outside allowed range "
                        f"[{COMPONENT_SCORE_MIN}, {COMPONENT_SCORE_MAX}]."
                    )
            except (ValueError, TypeError):
                errors.append(f"Row {idx}: '{col}' has non-integer value {val}.")
    return errors


def _validate_total_scores(df: pd.DataFrame) -> list[str]:
    """Validates total score boundaries and sum consistency."""
    errors: list[str] = []
    for idx, val in df["total_score"].dropna().items():
        try:
            int_val = int(val)
            if int_val != val or not (TOTAL_SCORE_MIN <= int_val <= TOTAL_SCORE_MAX):
                errors.append(
                    f"Row {idx}: 'total_score' value {val} is outside allowed range "
                    f"[{TOTAL_SCORE_MIN}, {TOTAL_SCORE_MAX}]."
                )
        except (ValueError, TypeError):
            errors.append(f"Row {idx}: 'total_score' has non-integer value {val}.")

    cols = list(COMPONENT_SCORE_COLUMNS) + ["total_score"]
    score_subset = df[cols].dropna()
    for idx, row in score_subset.iterrows():
        try:
            expected_sum = (
                int(row["correctness_score"])
                + int(row["completeness_score"])
                + int(row["communication_score"])
            )
            c_total = int(row["total_score"])
            if c_total != expected_sum:
                errors.append(
                    f"Row {idx}: 'total_score' ({c_total}) inconsistent with sum of components "
                    f"({int(row['correctness_score'])} + {int(row['completeness_score'])} + "
                    f"{int(row['communication_score'])} = {expected_sum})."
                )
        except (ValueError, TypeError):
            pass
    return errors


def _validate_proposed_thresholds(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    """Checks proposed score-to-label mappings and returns (errors, warnings)."""
    errors: list[str] = []
    warnings: list[str] = [
        "Quality label verification uses PROPOSED score thresholds "
        "(0-3 Poor, 4-7 Needs Improvement, 8-11 Good, 12-15 Excellent). "
        "Note: These thresholds are SUBJECT TO FACULTY VALIDATION AND ANNOTATION CALIBRATION."
    ]
    for idx, row in df[["total_score", "quality_label"]].dropna().iterrows():
        try:
            c_total = int(row["total_score"])
            c_label = int(row["quality_label"])
            if TOTAL_SCORE_MIN <= c_total <= TOTAL_SCORE_MAX:
                expected_label = map_score_to_proposed_label(c_total)
                if c_label != expected_label:
                    errors.append(
                        f"Row {idx}: Proposed quality label mismatch: 'total_score' {c_total} "
                        f"maps to proposed label {expected_label} "
                        f"('{PROPOSED_LABEL_NAMES[expected_label]}'), but found label {c_label} "
                        f"('{PROPOSED_LABEL_NAMES.get(c_label, 'Unknown')}')."
                    )
        except (ValueError, TypeError):
            pass
    return errors, warnings


def _validate_identifiers_and_leakage(
    df: pd.DataFrame, check_split_group_match: bool, check_candidate_duplicates: bool
) -> list[str]:
    """Validates split_group equality and duplicate candidate responses."""
    errors: list[str] = []
    if check_split_group_match:
        mismatch_mask = df["split_group"] != df["question_id"]
        if mismatch_mask.any():
            bad_indices = df.index[mismatch_mask].tolist()
            errors.append(
                f"Split group mismatch in {len(bad_indices)} row(s) at index(es) {bad_indices[:5]}: "
                f"'split_group' must match 'question_id' to enforce question-level anti-leakage partitioning."
            )

    if check_candidate_duplicates:
        dup_mask = df.duplicated(subset=["question_id", "candidate_answer"], keep=False)
        if dup_mask.any():
            dup_indices = df.index[dup_mask].tolist()
            errors.append(
                f"Duplicate candidate response detected in {len(dup_indices)} row(s) at index(es) {dup_indices[:5]}. "
                "Each (question_id, candidate_answer) pair must be unique."
            )
    return errors


def validate_dataset(
    df: Any,
    allow_extra_columns: bool = False,
    check_proposed_thresholds: bool = True,
    check_candidate_duplicates: bool = True,
    check_split_group_match: bool = True,
    raise_on_error: bool = False,
) -> ValidationResult:
    """Validates an in-memory pandas DataFrame against the documented 19-field schema.

    Args:
        df: The pandas DataFrame to validate.
        allow_extra_columns: If False, rejects DataFrames with extra unexpected columns.
        check_proposed_thresholds: If True, checks quality_label matches proposed total_score mapping.
        check_candidate_duplicates: If True, flags duplicate (question_id, candidate_answer) pairs.
        check_split_group_match: If True, verifies split_group equals question_id.
        raise_on_error: If True, raises DatasetValidationError upon encountering validation errors.

    Returns:
        ValidationResult with validation status, list of errors, and warnings.

    Raises:
        DatasetValidationError: If validation fails and raise_on_error is True.
    """
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(df, pd.DataFrame):
        errors.append(f"Expected pandas DataFrame, got {type(df).__name__}.")
        result = ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        if raise_on_error:
            result.raise_if_invalid()
        return result

    if df.empty:
        errors.append("DataFrame is empty (0 rows). At least 1 row is required.")
        result = ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        if raise_on_error:
            result.raise_if_invalid()
        return result

    col_errors, missing = _validate_columns(df, allow_extra_columns)
    errors.extend(col_errors)
    if missing:
        result = ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        if raise_on_error:
            result.raise_if_invalid()
        return result

    errors.extend(_validate_nulls_and_blanks(df))
    errors.extend(_validate_taxonomy(df))
    errors.extend(_validate_component_scores(df))
    errors.extend(_validate_total_scores(df))

    if check_proposed_thresholds:
        thresh_errors, thresh_warnings = _validate_proposed_thresholds(df)
        errors.extend(thresh_errors)
        warnings.extend(thresh_warnings)

    errors.extend(
        _validate_identifiers_and_leakage(df, check_split_group_match, check_candidate_duplicates)
    )

    is_valid = len(errors) == 0
    result = ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)
    if raise_on_error:
        result.raise_if_invalid()
    return result
