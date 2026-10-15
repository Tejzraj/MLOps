# External Source Data Directory (`data/source/`)

This directory is reserved for local, uncommitted clones or archives of external source repositories used for interview question bank ingestion.

## Source Repository
- **Source:** [`Krishnagangwal/CS-Fundamentals`](https://github.com/Krishnagangwal/CS-Fundamentals)
- **Local Path:** `data/source/CS-Fundamentals`
- **License Status:** Unlicensed / Educational (`"license": null`).
- **Git Tracking:** All files within `data/source/*` are ignored by Git (enforced in `.gitignore`).

## Ingestion Workflow
Run the automated ingestion stage:
```bash
python src/data/ingest_source.py --source-dir data/source/CS-Fundamentals
```
This reads only machine-readable markdown and document text, extracts canonical technical questions across 8 domains, records provenance metadata, and outputs:
- `data/raw/question_bank.csv`
- `reports/data_readiness_report.json`
