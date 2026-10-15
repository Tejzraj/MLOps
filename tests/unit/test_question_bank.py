"""Unit tests for Question Bank ingestion, validation, splitting, and domain classification.

Tests parsing, deduplication, schema validation, zero-leakage group splitting,
feature extraction, and multi-class domain evaluation without relying on real external networks.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

import pandas as pd
import pytest

from src.data.ingest_source import (
    compute_normalized_group_id,
    extract_questions_from_docx,
    extract_questions_from_hr_prompts,
    extract_questions_from_readme_topics,
    extract_questions_from_system_design,
    ingest_all_sources,
)
from src.data.preprocess import group_aware_split
from src.data.validation import (
    DatasetValidationError,
    validate_question_bank_dataset,
)
from src.evaluation.evaluate import (
    evaluate_model,
)
from src.features.build_features import (
    fit_feature_pipeline,
    transform_features,
)
from src.models.train_baseline import train_model


@pytest.fixture
def sample_question_bank_df() -> pd.DataFrame:
    """Creates a minimal valid question bank DataFrame across multiple domains."""
    records = []
    domains = ["DSA", "Operating Systems", "Computer Networks", "DBMS and SQL"]
    for dom in domains:
        for j in range(1, 4):
            q_text = f"Explain core concept number {j} of {dom} in depth."
            qid = f"Q_{dom[:3].upper()}_{j:03d}"
            records.append(
                {
                    "question_id": qid,
                    "question": q_text,
                    "domain": dom,
                    "reference_answer": f"Reference answer for {qid}.",
                    "source_repo": "https://github.com/Krishnagangwal/CS-Fundamentals",
                    "source_file": f"{dom}/README.md",
                    "extraction_method": "markdown_bullet_topic",
                    "license_status": "unlicensed_educational",
                    "group_id": compute_normalized_group_id(q_text),
                }
            )
    return pd.DataFrame(records)


def test_question_bank_validation_valid(sample_question_bank_df: pd.DataFrame) -> None:
    """Verifies that a conformant Question Bank DataFrame passes validation."""
    result = validate_question_bank_dataset(sample_question_bank_df, raise_on_error=True)
    assert result.is_valid
    assert len(result.errors) == 0


def test_question_bank_validation_missing_columns(sample_question_bank_df: pd.DataFrame) -> None:
    """Verifies that missing columns raise DatasetValidationError."""
    dropped = sample_question_bank_df.drop(columns=["domain"])
    with pytest.raises(DatasetValidationError, match="Missing required question bank columns"):
        validate_question_bank_dataset(dropped, raise_on_error=True)


def test_question_bank_validation_nulls(sample_question_bank_df: pd.DataFrame) -> None:
    """Verifies that nulls in required columns raise DatasetValidationError."""
    df_with_null = sample_question_bank_df.copy()
    df_with_null.loc[0, "question"] = None
    with pytest.raises(DatasetValidationError, match="Column 'question' has 1 null value"):
        validate_question_bank_dataset(df_with_null, raise_on_error=True)


def test_question_bank_validation_invalid_domain(sample_question_bank_df: pd.DataFrame) -> None:
    """Verifies that unapproved domain names are rejected."""
    df_invalid = sample_question_bank_df.copy()
    df_invalid.loc[0, "domain"] = "Quantum Computing"
    with pytest.raises(DatasetValidationError, match="Invalid domain"):
        validate_question_bank_dataset(df_invalid, raise_on_error=True)


def test_question_bank_validation_short_question(sample_question_bank_df: pd.DataFrame) -> None:
    """Verifies that questions shorter than 10 characters are rejected."""
    df_short = sample_question_bank_df.copy()
    df_short.loc[0, "question"] = "Why?"
    with pytest.raises(DatasetValidationError, match="shorter than 10 characters"):
        validate_question_bank_dataset(df_short, raise_on_error=True)


def test_question_bank_validation_duplicate_id(sample_question_bank_df: pd.DataFrame) -> None:
    """Verifies that duplicate question_ids are flagged."""
    df_dup = sample_question_bank_df.copy()
    df_dup.loc[1, "question_id"] = df_dup.loc[0, "question_id"]
    with pytest.raises(DatasetValidationError, match="Duplicate question_id"):
        validate_question_bank_dataset(df_dup, raise_on_error=True)


def test_compute_normalized_group_id() -> None:
    """Verifies deterministic stem hashing ignores punctuation, casing, and spacing."""
    t1 = "How do you reverse a Linked List?"
    t2 = "how do you reverse a linked list"
    t3 = "  How   do you  reverse a  linked-list???  "
    h1 = compute_normalized_group_id(t1)
    h2 = compute_normalized_group_id(t2)
    h3 = compute_normalized_group_id(t3)
    assert h1 == h2 == h3
    assert len(h1) == 12


def test_group_aware_split_zero_leakage(sample_question_bank_df: pd.DataFrame) -> None:
    """Verifies zero question-group leakage between train, val, and test splits."""
    train_df, val_df, test_df = group_aware_split(
        df=sample_question_bank_df,
        group_column="group_id",
        test_size=0.25,
        val_size=0.25,
        random_state=42,
    )
    train_groups = set(train_df["group_id"])
    val_groups = set(val_df["group_id"])
    test_groups = set(test_df["group_id"])

    assert len(train_groups & val_groups) == 0, "Train and Val groups must not overlap!"
    assert len(train_groups & test_groups) == 0, "Train and Test groups must not overlap!"
    assert len(val_groups & test_groups) == 0, "Val and Test groups must not overlap!"
    assert len(train_df) + len(val_df) + len(test_df) == len(sample_question_bank_df)


def test_feature_pipeline_train_only(sample_question_bank_df: pd.DataFrame) -> None:
    """Verifies that TF-IDF feature pipeline fits strictly on training questions."""
    train_df, _, test_df = group_aware_split(
        df=sample_question_bank_df,
        group_column="group_id",
        test_size=0.25,
        val_size=0.25,
        random_state=42,
    )
    vectorizer = fit_feature_pipeline(train_df, tfidf_params={"min_df": 1})
    x_train, y_train = transform_features(train_df, vectorizer, target_column="domain")
    x_test, y_test = transform_features(test_df, vectorizer, target_column="domain")

    assert x_train.shape[0] == len(train_df)
    assert x_test.shape[0] == len(test_df)
    assert x_train.shape[1] == x_test.shape[1]
    assert len(y_train) == len(train_df)
    assert len(y_test) == len(test_df)


def test_model_training_and_evaluation_domain(
    tmp_path: Path, sample_question_bank_df: pd.DataFrame
) -> None:
    """Tests training and evaluation workflow with multi-class domain target labels."""
    train_df, val_df, test_df = group_aware_split(
        df=sample_question_bank_df,
        group_column="group_id",
        test_size=0.25,
        val_size=0.25,
        random_state=42,
    )

    proc_dir = tmp_path / "processed"
    proc_dir.mkdir(parents=True)
    train_path = proc_dir / "train.parquet"
    test_path = proc_dir / "test.parquet"
    train_df.to_parquet(train_path, index=False)
    test_df.to_parquet(test_path, index=False)

    import joblib

    vec_dir = tmp_path / "models"
    vec_dir.mkdir(parents=True)
    vec_path = vec_dir / "tfidf_vectorizer.joblib"
    mod_path = vec_dir / "baseline_model.joblib"

    vectorizer = fit_feature_pipeline(train_df, tfidf_params={"min_df": 1})
    joblib.dump(vectorizer, vec_path)

    clf = train_model(
        train_path=train_path,
        vectorizer_path=vec_path,
        output_model_path=mod_path,
        algorithm="logistic_regression",
        model_params={"c_param": 1.0, "max_iter": 500},
        track_with_mlflow=False,
        target_column="domain",
    )
    assert clf is not None
    assert mod_path.is_file()

    # Evaluate
    metrics_path = tmp_path / "reports" / "metrics.json"
    fig_path = tmp_path / "reports" / "confusion_matrix.png"

    results = evaluate_model(
        test_path=test_path,
        model_path=mod_path,
        vectorizer_path=vec_path,
        metrics_output_path=metrics_path,
        figure_output_path=fig_path,
        track_with_mlflow=False,
        target_column="domain",
    )

    assert "accuracy" in results
    assert "f1_macro" in results
    assert "confusion_matrix" in results
    assert metrics_path.is_file()
    assert fig_path.is_file()


def test_extract_questions_from_system_design(tmp_path: Path) -> None:
    """Tests extraction of numbered design problems from cheatsheet markdown."""
    md_file = tmp_path / "System-Design-Cheatsheet.md"
    content = (
        "# System Design\n\n"
        "## Top 31 Component Design Problems\n\n"
        "1. Top K Frequent Elements in Recent X mins\n"
        "2. Design an API Rate Limiter\n"
        "3. Design: Leaderboard Ranking\n"
        "---\n\n"
        "## Other Notes\n"
    )
    md_file.write_text(content, encoding="utf-8")
    extracted = extract_questions_from_system_design(md_file)
    assert len(extracted) == 3
    assert extracted[0]["domain"] == "System Design"
    assert "Top K Frequent Elements" in extracted[0]["question"]


def test_extract_questions_from_hr_prompts(tmp_path: Path) -> None:
    """Tests extraction of numbered interview preparation prompts."""
    md_file = tmp_path / "25-Job-Interview-Preparation-Prompts.md"
    content = (
        "# Prompts\n\n"
        "1. Can you provide common interview questions for software engineering?\n"
        "2. How should I prepare for a behavioral interview using STAR method?\n"
    )
    md_file.write_text(content, encoding="utf-8")
    extracted = extract_questions_from_hr_prompts(md_file)
    assert len(extracted) == 2
    assert extracted[0]["domain"] == "HR / Behavioural"


def test_extract_questions_from_readme_topics(tmp_path: Path) -> None:
    """Tests bullet topic extraction and filtering of short/URL lines."""
    md_file = tmp_path / "README.md"
    content = (
        "# OS\n\n"
        "## Topics to Cover\n"
        "- What is an Operating System?\n"
        "- Process vs Thread\n"
        "- Mutex\n"  # short item (< 8 chars)
        "- https://example.com/os-resource\n"  # url item
        "## Resources\n"
        "- Ignore this section\n"
    )
    md_file.write_text(content, encoding="utf-8")
    extracted, ambiguous = extract_questions_from_readme_topics(
        md_file, "Operating Systems", "Operating-System/README.md"
    )
    assert len(extracted) == 2
    assert len(ambiguous) == 2
    assert extracted[0]["domain"] == "Operating Systems"


def test_extract_questions_from_docx_mock(tmp_path: Path) -> None:
    """Tests extraction of numbered paragraphs from a mock docx zip file."""
    docx_file = tmp_path / "test.docx"
    xml_data = (
        b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        b'<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        b"<w:body>"
        b"<w:p><w:t>Top 50 DSA Questions</w:t></w:p>"
        b"<w:p><w:t>1. How do you find the missing number in a given array of 1 to 100?</w:t></w:p>"
        b"<w:p><w:t>2. How do you find the duplicate number on a given integer array?</w:t></w:p>"
        b"</w:body></w:document>"
    )
    with zipfile.ZipFile(docx_file, "w") as z:
        z.writestr("word/document.xml", xml_data)

    extracted = extract_questions_from_docx(docx_file)
    assert len(extracted) == 2
    assert extracted[0]["domain"] == "DSA"
    assert "missing number" in extracted[0]["question"]


def test_ingest_all_sources_missing_dir(tmp_path: Path) -> None:
    """Verifies FileNotFoundError when source directory does not exist."""
    missing = tmp_path / "nonexistent_source"
    with pytest.raises(FileNotFoundError, match="Source directory not found"):
        ingest_all_sources(missing)


def test_ingest_all_sources_mock(tmp_path: Path) -> None:
    """Tests end-to-end ingestion from mock directory structure."""
    src_dir = tmp_path / "mock_cs"
    (src_dir / "DSA").mkdir(parents=True)
    (src_dir / "System-Design").mkdir(parents=True)
    (src_dir / "Operating-System").mkdir(parents=True)
    (src_dir / "DBMS-and-SQL").mkdir(parents=True)
    (src_dir / "OOPs").mkdir(parents=True)
    (src_dir / "Software-Engineering").mkdir(parents=True)
    (src_dir / "Computer-Network").mkdir(parents=True)

    # Mock docx
    xml_data = (
        b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        b'<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        b"<w:body>"
        b"<w:p><w:t>1. How do you reverse a linked list in place?</w:t></w:p>"
        b"</w:body></w:document>"
    )
    with zipfile.ZipFile(src_dir / "DSA" / "Top-50-DSA-Interview-Questions.docx", "w") as z:
        z.writestr("word/document.xml", xml_data)

    # Mock system design
    (src_dir / "System-Design" / "System-Design-Cheatsheet.md").write_text(
        "## Top 31 Component Design Problems\n1. Design an API Rate Limiter\n---\n",
        encoding="utf-8",
    )

    # Mock HR
    (src_dir / "25-Job-Interview-Preparation-Prompts.md").write_text(
        "1. Tell me about a time you solved a technical conflict.\n", encoding="utf-8"
    )

    # Mock READMEs
    (src_dir / "Operating-System" / "README.md").write_text(
        "- What is an Operating System?\n", encoding="utf-8"
    )
    (src_dir / "DBMS-and-SQL" / "README.md").write_text(
        "- Normalization (1NF, 2NF, 3NF)\n", encoding="utf-8"
    )
    (src_dir / "OOPs" / "README.md").write_text(
        "- Encapsulation vs Abstraction\n", encoding="utf-8"
    )
    (src_dir / "Software-Engineering" / "README.md").write_text(
        "- Agile vs Waterfall model\n", encoding="utf-8"
    )
    (src_dir / "Computer-Network" / "CN-Roadmap.md").write_text(
        "- OSI Model vs TCP/IP Model\n", encoding="utf-8"
    )
    (src_dir / "DSA" / "README.md").write_text(
        "- Dynamic Programming vs Greedy\n", encoding="utf-8"
    )

    df, stats = ingest_all_sources(src_dir)
    assert len(df) >= 8
    assert "timestamp" in stats
    assert stats["valid_records"] == len(df)
    assert stats["duplicate_records_removed"] == 0
