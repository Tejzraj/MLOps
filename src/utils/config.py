"""Configuration loaders, logging helpers, and data hashing utilities.

Provides centralized helpers for reading YAML configuration files,
setting up standard logging, and computing deterministic SHA256 hashes
of datasets for data lineage and MLflow tracking.
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

DEFAULT_PARAMS_PATH = Path("params.yaml")
DEFAULT_CONFIG_PATH = Path("configs/config.yaml")


def load_params(params_path: str | Path = DEFAULT_PARAMS_PATH) -> dict[str, Any]:
    """Loads pipeline parameters from a YAML file.

    Args:
        params_path: Path to params.yaml file.

    Returns:
        Dictionary containing parameter hierarchy.

    Raises:
        FileNotFoundError: If the specified parameter file does not exist.
        ValueError: If the file is empty or not valid YAML.
    """
    path = Path(params_path)
    if not path.is_file():
        raise FileNotFoundError(f"Parameters file not found at '{path.resolve()}'.")

    with path.open("r", encoding="utf-8") as f:
        params = yaml.safe_load(f)

    if not isinstance(params, dict):
        raise ValueError(f"Parameters file '{path}' is empty or does not parse to a dictionary.")

    return params


def load_config(config_path: str | Path = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    """Loads system configuration from a YAML file.

    Args:
        config_path: Path to configs/config.yaml file.

    Returns:
        Dictionary containing system configuration.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
        ValueError: If the file is empty or not valid YAML.
    """
    path = Path(config_path)
    if not path.is_file():
        raise FileNotFoundError(f"Configuration file not found at '{path.resolve()}'.")

    with path.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if not isinstance(config, dict):
        raise ValueError(f"Configuration file '{path}' is empty or does not parse to a dictionary.")

    return config


def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Configures and returns a structured logger.

    Args:
        name: Name of the logger (typically __name__).
        level: Logging level string ('DEBUG', 'INFO', 'WARNING', 'ERROR').

    Returns:
        Configured logging.Logger instance.
    """
    logger = logging.getLogger(name)
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def compute_data_fingerprint(data: pd.DataFrame | Path | str) -> str:
    """Computes a deterministic SHA256 hex digest for a DataFrame or file.

    Used for data lineage, MLflow dataset tagging, and artifact verification.

    Args:
        data: Either a pandas DataFrame, a Path, or a string path.

    Returns:
        64-character SHA256 hex string.
    """
    hasher = hashlib.sha256()

    if isinstance(data, pd.DataFrame):
        # Hash stable CSV representation without index
        csv_bytes = data.to_csv(index=False).encode("utf-8")
        hasher.update(csv_bytes)
    else:
        path = Path(data)
        if not path.is_file():
            raise FileNotFoundError(f"Cannot compute fingerprint: file '{path}' not found.")
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)

    return hasher.hexdigest()
