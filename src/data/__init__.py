"""Data loading, cleaning, validation, and splitting module.

Contains functions and scripts to ingest raw interview QA datasets,
validate schemas, clean textual content, and generate reproducible splits.
"""

from src.data.load_data import load_and_validate_data
from src.data.preprocess import (
    group_aware_split,
    normalize_text_conservatively,
    preprocess_data,
)
from src.data.validation import (
    ALLOWED_DIFFICULTIES,
    ALLOWED_DOMAINS,
    ALLOWED_QUALITY_LABELS,
    ALLOWED_QUESTION_TYPES,
    CANONICAL_DOMAINS,
    PROPOSED_LABEL_MAPPING,
    QUESTION_BANK_DOMAINS,
    QUESTION_BANK_SCHEMA_COLUMNS,
    SCHEMA_COLUMNS,
    DatasetValidationError,
    ValidationResult,
    map_score_to_proposed_label,
    validate_dataset,
    validate_question_bank_dataset,
)

__all__ = [
    "ALLOWED_DIFFICULTIES",
    "ALLOWED_DOMAINS",
    "ALLOWED_QUALITY_LABELS",
    "ALLOWED_QUESTION_TYPES",
    "CANONICAL_DOMAINS",
    "PROPOSED_LABEL_MAPPING",
    "QUESTION_BANK_DOMAINS",
    "QUESTION_BANK_SCHEMA_COLUMNS",
    "SCHEMA_COLUMNS",
    "DatasetValidationError",
    "ValidationResult",
    "group_aware_split",
    "load_and_validate_data",
    "map_score_to_proposed_label",
    "normalize_text_conservatively",
    "preprocess_data",
    "validate_dataset",
    "validate_question_bank_dataset",
]
