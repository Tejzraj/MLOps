"""Data loading and schema validation stage for Phase 1 MLOps pipeline.

Reads local raw dataset, validates schema and taxonomy against documented
specifications, and writes validated dataset to interim Parquet storage.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.data.validation import validate_dataset
from src.utils.config import compute_data_fingerprint, get_logger, load_params

logger = get_logger("src.data.load_data")


def load_and_validate_data(
    raw_path: str | Path,
    output_path: str | Path,
    allow_extra_columns: bool = False,
    check_proposed_thresholds: bool = True,
) -> pd.DataFrame:
    """Loads a local CSV dataset, validates it against schema rules, and saves to Parquet.

    Args:
        raw_path: Path to the raw CSV dataset file.
        output_path: Path where the validated interim Parquet file will be written.
        allow_extra_columns: Whether to allow extra columns beyond the 19 schema fields.
        check_proposed_thresholds: Whether to verify proposed quality label mappings.

    Returns:
        The validated pandas DataFrame.

    Raises:
        FileNotFoundError: If the raw data file does not exist.
        DatasetValidationError: If validation against schema rules fails.
    """
    raw_file = Path(raw_path)
    out_file = Path(output_path)

    if not raw_file.is_file():
        raise FileNotFoundError(
            f"Raw dataset not found at '{raw_file.resolve()}'. "
            "Please ensure the approved interview QA dataset is placed at this path."
        )

    logger.info(f"Loading raw dataset from '{raw_file}'...")
    df = pd.read_csv(raw_file)
    logger.info(f"Loaded {len(df)} rows and {len(df.columns)} columns.")

    # Canonicalize legacy column aliases if present
    if "interview_question" in df.columns and "question" not in df.columns:
        logger.info("Aliasing column 'interview_question' -> 'question' to match schema.")
        df = df.rename(columns={"interview_question": "question"})

    # Validate against documented schema
    logger.info("Validating dataset against 19-field schema...")
    validate_dataset(
        df,
        allow_extra_columns=allow_extra_columns,
        check_proposed_thresholds=check_proposed_thresholds,
        raise_on_error=True,
    )
    logger.info("Schema validation passed successfully.")

    # Write to interim storage
    out_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_file, index=False)
    fingerprint = compute_data_fingerprint(df)
    logger.info(f"Saved interim dataset to '{out_file}' (SHA256: {fingerprint[:12]}...).")

    return df


def main() -> None:
    """CLI entrypoint for DVC load_data stage."""
    parser = argparse.ArgumentParser(description="Load and validate raw interview QA dataset.")
    parser.add_argument("--input", type=str, default=None, help="Path to input raw CSV dataset.")
    parser.add_argument(
        "--output",
        type=str,
        default="data/interim/loaded_data.parquet",
        help="Path to output interim Parquet file.",
    )
    args = parser.parse_args()

    params = load_params()
    raw_path = args.input or params.get("data", {}).get(
        "raw_data_path", "data/raw/interview_data.csv"
    )

    load_and_validate_data(raw_path=raw_path, output_path=args.output)


if __name__ == "__main__":
    main()
