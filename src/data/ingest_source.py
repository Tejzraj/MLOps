"""Source data ingestion and question bank extraction module.

Audits and ingests interview-question material from local clone of
Krishnagangwal/CS-Fundamentals, extracts structured questions across
8 canonical technical domains, records provenance metadata, and outputs
a validated question bank dataset and data readiness report.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import xml.etree.ElementTree as ET
import zipfile
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Ensure project root is in sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pandas as pd

from src.data.validation import (
    QUESTION_BANK_DOMAINS,
    validate_question_bank_dataset,
)
from src.utils.config import compute_data_fingerprint, get_logger, load_params

logger = get_logger("src.data.ingest_source")

SOURCE_REPO_URL = "https://github.com/Krishnagangwal/CS-Fundamentals"
DEFAULT_LICENSE_STATUS = "unlicensed_educational"

# Domain mapping for ID prefixing
DOMAIN_PREFIXES: dict[str, str] = {
    "Computer Networks": "CN",
    "DBMS and SQL": "DBMS",
    "DSA": "DSA",
    "HR / Behavioural": "HR",
    "OOP": "OOP",
    "Operating Systems": "OS",
    "Software Engineering": "SE",
    "System Design": "SYS",
}


def compute_normalized_group_id(text: str) -> str:
    """Computes a deterministic group identifier from normalized question text.

    Used to group duplicate or near-identical question variants together
    for leakage-safe dataset partitioning.

    Args:
        text: Raw question string.

    Returns:
        12-character MD5 hash of normalized question stem.
    """
    stem = re.sub(r"[^a-z0-9]", "", text.lower())
    return hashlib.md5(stem.encode("utf-8")).hexdigest()[:12]


def extract_questions_from_docx(docx_path: Path) -> list[dict[str, Any]]:
    """Extracts numbered interview questions from a Word .docx document.

    Parses word/document.xml directly without external heavy dependencies.

    Args:
        docx_path: Path to the .docx file.

    Returns:
        List of extracted question dictionaries.
    """
    if not docx_path.is_file():
        logger.warning(f"DOCX file not found: {docx_path}")
        return []

    with zipfile.ZipFile(docx_path) as z:
        xml_content = z.read("word/document.xml")

    tree = ET.fromstring(xml_content)
    namespaces = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

    extracted = []
    for p in tree.iterfind(".//w:p", namespaces):
        text = "".join(node.text for node in p.iterfind(".//w:t", namespaces) if node.text)
        text = text.strip()
        if not text:
            continue

        # Match numbered questions (e.g. "1. How do you find...", "10. How are duplicates...")
        m = re.match(r"^(?:\d+\.|\d+\))\s*(.+)", text)
        if m:
            cand = m.group(1).strip()
            # Exclude section headers like "Array Coding Interview Questions"
            if len(cand) >= 15 and not any(
                cand.startswith(h)
                for h in ["Array", "Linked List", "String", "Binary Tree", "Miscellaneous"]
            ):
                extracted.append(
                    {
                        "domain": "DSA",
                        "question": cand,
                        "source_file": "DSA/Top-50-DSA-Interview-Questions.docx",
                        "extraction_method": "docx_numbered_paragraph",
                    }
                )
        elif "How do you check if two strings are a rotation" in text:
            extracted.append(
                {
                    "domain": "DSA",
                    "question": "How do you check if two strings are a rotation of each other?",
                    "source_file": "DSA/Top-50-DSA-Interview-Questions.docx",
                    "extraction_method": "docx_numbered_paragraph",
                }
            )

    return extracted


def extract_questions_from_system_design(md_path: Path) -> list[dict[str, Any]]:
    """Extracts component design questions from System-Design-Cheatsheet.md.

    Args:
        md_path: Path to System-Design-Cheatsheet.md.

    Returns:
        List of extracted question dictionaries.
    """
    if not md_path.is_file():
        logger.warning(f"System design markdown not found: {md_path}")
        return []

    with open(md_path, encoding="utf-8", errors="ignore") as f:
        text = f.read()

    extracted = []
    start = False
    for line in text.splitlines():
        if "Top 31 Component Design Problems" in line:
            start = True
            continue
        if start and line.startswith("---"):
            break
        if start:
            m = re.match(r"^\d+\.\s*(.+)", line.strip())
            if m:
                q_text = m.group(1).strip()
                if not q_text.lower().startswith(
                    (
                        "how",
                        "what",
                        "design",
                        "implement",
                        "store",
                        "support",
                        "avoid",
                        "find",
                        "deploy",
                        "merge",
                    )
                ):
                    q_text = f"How would you {q_text}?"
                extracted.append(
                    {
                        "domain": "System Design",
                        "question": q_text,
                        "source_file": "System-Design/System-Design-Cheatsheet.md",
                        "extraction_method": "markdown_numbered_list",
                    }
                )

    return extracted


def extract_questions_from_hr_prompts(md_path: Path) -> list[dict[str, Any]]:
    """Extracts interview questions from 25-Job-Interview-Preparation-Prompts.md.

    Args:
        md_path: Path to 25-Job-Interview-Preparation-Prompts.md.

    Returns:
        List of extracted question dictionaries.
    """
    if not md_path.is_file():
        logger.warning(f"HR prompts markdown not found: {md_path}")
        return []

    with open(md_path, encoding="utf-8", errors="ignore") as f:
        text = f.read()

    extracted = []
    for line in text.splitlines():
        m = re.match(r"^\d+\.\s*(.+)", line.strip())
        if m:
            extracted.append(
                {
                    "domain": "HR / Behavioural",
                    "question": m.group(1).strip(),
                    "source_file": "25-Job-Interview-Preparation-Prompts.md",
                    "extraction_method": "markdown_numbered_list",
                }
            )

    return extracted


def extract_questions_from_readme_topics(
    md_path: Path, domain: str, rel_path: str
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Extracts topic concepts as interview questions from subject README.md files.

    Args:
        md_path: Path to subject README.md.
        domain: Canonical domain name.
        rel_path: Relative file path for provenance.

    Returns:
        Tuple of (extracted_records, ambiguous_records).
    """
    if not md_path.is_file():
        logger.warning(f"Subject README not found: {md_path}")
        return [], []

    with open(md_path, encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    extracted = []
    ambiguous = []

    for line in lines:
        line_s = line.strip()
        if line_s.startswith("## Resources") or line_s.startswith("## Reference"):
            break
        if line_s.startswith("- ") or line_s.startswith("* "):
            item = line_s[2:].strip()
            item = re.sub(r"\*\*([^*]+)\*\*", r"\1", item)
            item = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", item)
            item = re.sub(r"`([^`]+)`", r"\1", item)

            if item.startswith("http") or len(item) < 8:
                ambiguous.append(
                    {"text": item, "domain": domain, "file": rel_path, "reason": "too short or URL"}
                )
                continue

            # Format item as interview question prompt
            if not item.endswith("?") and not item.lower().startswith(
                (
                    "what",
                    "how",
                    "why",
                    "explain",
                    "compare",
                    "difference",
                    "describe",
                    "can",
                    "implement",
                    "design",
                )
            ):
                q_text = f"Explain {item} in the context of {domain}."
            else:
                q_text = item

            extracted.append(
                {
                    "domain": domain,
                    "question": q_text,
                    "source_file": rel_path,
                    "extraction_method": "markdown_bullet_topic",
                }
            )

    return extracted, ambiguous


def ingest_all_sources(source_dir: str | Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Audits local source files, extracts interview questions, and creates a DataFrame.

    Args:
        source_dir: Path to local CS-Fundamentals source directory.

    Returns:
        Tuple of (validated_dataframe, audit_statistics_dict).

    Raises:
        FileNotFoundError: If source_dir does not exist.
        DatasetValidationError: If the extracted dataset fails schema validation.
    """
    src_path = Path(source_dir)
    if not src_path.is_dir():
        raise FileNotFoundError(
            f"Source directory not found at '{src_path.resolve()}'. "
            "Please ensure Krishnagangwal/CS-Fundamentals is placed at this path."
        )

    all_raw_records: list[dict[str, Any]] = []
    all_ambiguous: list[dict[str, Any]] = []

    # 1. DSA Docx
    dsa_docx = src_path / "DSA" / "Top-50-DSA-Interview-Questions.docx"
    all_raw_records.extend(extract_questions_from_docx(dsa_docx))

    # 2. System Design
    sd_md = src_path / "System-Design" / "System-Design-Cheatsheet.md"
    all_raw_records.extend(extract_questions_from_system_design(sd_md))

    # 3. HR Prompts
    hr_md = src_path / "25-Job-Interview-Preparation-Prompts.md"
    all_raw_records.extend(extract_questions_from_hr_prompts(hr_md))

    # 4. Subject READMEs
    readme_specs = [
        ("Operating-System/README.md", "Operating Systems"),
        ("DBMS-and-SQL/README.md", "DBMS and SQL"),
        ("OOPs/README.md", "OOP"),
        ("Software-Engineering/README.md", "Software Engineering"),
        ("Computer-Network/CN-Roadmap.md", "Computer Networks"),
        ("DSA/README.md", "DSA"),
    ]

    for rel_f, dom in readme_specs:
        rec, amb = extract_questions_from_readme_topics(src_path / rel_f, dom, rel_f)
        all_raw_records.extend(rec)
        all_ambiguous.extend(amb)

    total_extracted = len(all_raw_records)
    logger.info(f"Total raw items extracted: {total_extracted}")

    # Deduplication while preserving provenance
    seen_stems: set[str] = set()
    deduped_records: list[dict[str, Any]] = []
    duplicate_count = 0

    # Sort deterministically by domain and question
    all_raw_records.sort(key=lambda r: (r["domain"], r["question"]))

    domain_counters: dict[str, int] = dict.fromkeys(QUESTION_BANK_DOMAINS, 0)

    for item in all_raw_records:
        q_text = item["question"].strip()
        stem = compute_normalized_group_id(q_text)
        if stem in seen_stems:
            duplicate_count += 1
            continue
        seen_stems.add(stem)

        dom = item["domain"]
        domain_counters[dom] += 1
        prefix = DOMAIN_PREFIXES.get(dom, "GEN")
        q_id = f"Q_{prefix}_{domain_counters[dom]:03d}"

        deduped_records.append(
            {
                "question_id": q_id,
                "question": q_text,
                "domain": dom,
                "reference_answer": "",
                "source_repo": SOURCE_REPO_URL,
                "source_file": item["source_file"],
                "extraction_method": item["extraction_method"],
                "license_status": DEFAULT_LICENSE_STATUS,
                "group_id": stem,
            }
        )

    df = pd.DataFrame(deduped_records)
    logger.info(
        f"Deduplication complete: {len(df)} unique records retained ({duplicate_count} duplicates removed)."
    )

    # Validate against Question Bank schema
    validate_question_bank_dataset(df, raise_on_error=True)

    fingerprint = compute_data_fingerprint(df)
    domain_dist = dict(Counter(df["domain"]))

    stats = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_repo": SOURCE_REPO_URL,
        "license_status": DEFAULT_LICENSE_STATUS,
        "total_extracted_records": total_extracted,
        "valid_records": len(df),
        "duplicate_records_removed": duplicate_count,
        "excluded_ambiguous_records": len(all_ambiguous),
        "domain_distribution": domain_dist,
        "ambiguous_examples": all_ambiguous[:10],
        "data_fingerprint_sha256": fingerprint,
    }

    return df, stats


def main() -> None:
    """CLI entrypoint for DVC ingest_source stage."""
    parser = argparse.ArgumentParser(description="Ingest source questions from CS-Fundamentals.")
    parser.add_argument(
        "--source-dir",
        type=str,
        default="data/source/CS-Fundamentals",
        help="Path to CS-Fundamentals source repository.",
    )
    parser.add_argument(
        "--output-csv",
        type=str,
        default="data/raw/question_bank.csv",
        help="Path to output raw CSV dataset.",
    )
    parser.add_argument(
        "--report-json",
        type=str,
        default="reports/data_readiness_report.json",
        help="Path to output data readiness JSON report.",
    )
    args = parser.parse_args()

    params = load_params()
    source_dir = params.get("data", {}).get("source_dir", args.source_dir)
    output_csv = params.get("data", {}).get("raw_data_path", args.output_csv)

    out_csv_path = Path(output_csv)
    out_rep_path = Path(args.report_json)

    out_csv_path.parent.mkdir(parents=True, exist_ok=True)
    out_rep_path.parent.mkdir(parents=True, exist_ok=True)

    df, stats = ingest_all_sources(source_dir=source_dir)

    df.to_csv(out_csv_path, index=False)
    logger.info(f"Saved {len(df)} questions to '{out_csv_path}'.")

    with open(out_rep_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    logger.info(f"Saved data readiness report to '{out_rep_path}'.")


if __name__ == "__main__":
    main()
