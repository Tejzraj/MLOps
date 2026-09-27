# Test Suite Specification

> **Project:** AI-Based Interview Preparation Assistant  
> **Course:** AI252TA – Machine Learning Operations | Semester V  
> **Framework:** PyTest  

---

## 1. Testing Strategy

The test suite enforces software reliability, data integrity, and model verification across the entire lifecycle:

```text
tests/
├── unit/               # Fast, isolated unit tests for individual functions
│   ├── test_data.py            # Data loading, validation, and split functions
│   ├── test_features.py        # Text vectorizers and feature transformers
│   └── test_utils.py           # Configuration loading and utility helpers
├── integration/        # Pipeline stage execution tests
│   └── test_pipeline.py        # End-to-end data-to-evaluation pipeline verification
├── model/              # Model quality, behavioral, and invariance tests (Phase 2)
│   ├── test_invariance.py      # Linguistic invariance and sensitivity tests
│   └── test_benchmarks.py      # Minimum performance thresholds (e.g. F1 >= baseline)
└── README.md           # Test suite architecture and instructions
```

---

## 2. Running Tests

Execute the complete test suite locally:

```bash
# Run tests with coverage report
make test

# Or directly with pytest
pytest -v --cov=src --cov-report=term-missing
```

---

## 3. Test Standards & CI Integration

- **Determinism:** Tests must be seed-deterministic and run without external internet dependencies.
- **Coverage Target:** Minimum target of $\ge 80\%$ test coverage on core `src/` modules.
- **Pre-commit & CI:** All tests run automatically on Pull Requests via GitHub Actions CI in Phase 2.
