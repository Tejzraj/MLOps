"""Unit tests for utility functions: config loading, data hashing, and logging."""

from __future__ import annotations

import pandas as pd
import pytest

from src.utils.config import (
    compute_data_fingerprint,
    get_logger,
    load_config,
    load_params,
)


def test_load_params_valid() -> None:
    """Verifies that params.yaml loads correctly as a dictionary."""
    params = load_params("params.yaml")
    assert isinstance(params, dict)
    assert "data" in params
    assert "split" in params
    assert "features" in params
    assert "model" in params


def test_load_params_missing(tmp_path: pytest.TempPathFactory) -> None:
    """Verifies FileNotFoundError when parameter file does not exist."""
    missing = tmp_path / "nonexistent_params.yaml"
    with pytest.raises(FileNotFoundError):
        load_params(missing)


def test_load_config_valid() -> None:
    """Verifies that configs/config.yaml loads correctly."""
    cfg = load_config("configs/config.yaml")
    assert isinstance(cfg, dict)
    assert "app" in cfg
    assert "paths" in cfg
    assert "mlflow" in cfg


def test_compute_data_fingerprint_deterministic() -> None:
    """Verifies that compute_data_fingerprint produces identical SHA256 for identical DataFrames."""
    df1 = pd.DataFrame([{"a": 1, "b": "text"}])
    df2 = pd.DataFrame([{"a": 1, "b": "text"}])
    df3 = pd.DataFrame([{"a": 2, "b": "text"}])

    hash1 = compute_data_fingerprint(df1)
    hash2 = compute_data_fingerprint(df2)
    hash3 = compute_data_fingerprint(df3)

    assert hash1 == hash2
    assert hash1 != hash3
    assert len(hash1) == 64


def test_get_logger() -> None:
    """Verifies that get_logger creates a logger with configured name."""
    logger = get_logger("test.custom_logger", level="DEBUG")
    assert logger.name == "test.custom_logger"
