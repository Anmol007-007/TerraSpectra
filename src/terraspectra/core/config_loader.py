"""YAML configuration loader with deep dictionary merge support."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge override dictionary into base dictionary.

    Args:
        base: The base dictionary.
        override: The dictionary with overriding keys and nested values.

    Returns:
        A new nested dictionary with merged values.
    """
    merged: dict[str, Any] = base.copy()
    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_yaml(file_path: str | Path) -> dict[str, Any]:
    """Load a YAML configuration file.

    Args:
        file_path: Path to the .yaml file.

    Returns:
        Parsed dictionary. Returns empty dict if file is empty.
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def load_merged_config(base_path: str | Path, *override_paths: str | Path) -> dict[str, Any]:
    """Load base YAML file and sequentially deep-merge optional override files.

    Args:
        base_path: Base config file path.
        *override_paths: Variable number of override YAML config file paths.

    Returns:
        Merged configuration dictionary.
    """
    config = load_yaml(base_path)
    for override_path in override_paths:
        override = load_yaml(override_path)
        config = deep_merge(config, override)
    return config
