"""Unit tests for settings and YAML config loading."""

from __future__ import annotations

from pathlib import Path

import pytest

from terraspectra.core.config_loader import deep_merge, load_merged_config, load_yaml
from terraspectra.core.settings import Settings


def test_default_settings() -> None:
    """Test default settings values."""
    s = Settings()
    assert s.env in ("development", "test", "production")
    assert s.device in ("auto", "cpu", "cuda")
    assert s.data_dir == Path("data")
    assert s.raw_data_dir == Path("data/raw")
    assert s.catalog_path == Path("data/catalog/scenes.json")


def test_deep_merge_simple() -> None:
    """Test recursive merging of nested dictionaries."""
    base = {"a": 1, "b": {"c": 2, "d": 3}}
    override = {"b": {"d": 99, "e": 4}, "f": 5}
    merged = deep_merge(base, override)
    assert merged["a"] == 1
    assert merged["b"]["c"] == 2
    assert merged["b"]["d"] == 99
    assert merged["b"]["e"] == 4
    assert merged["f"] == 5


def test_load_yaml_configs() -> None:
    """Test loading existing configuration YAML files."""
    default_cfg = load_yaml("configs/default.yaml")
    assert default_cfg["project"]["name"] == "terraspectra"
    assert default_cfg["system"]["seed"] == 42

    data_cfg = load_yaml("configs/data.yaml")
    assert data_cfg["sensor"]["n_bands"] == 224
    assert data_cfg["preprocessing"]["pca_components"] == 32

    model_cfg = load_yaml("configs/model.yaml")
    assert model_cfg["model"]["name"] == "HybridCNNViT"
    assert model_cfg["vit_backbone"]["d_model"] == 128


def test_load_merged_config(tmp_path: Path) -> None:
    """Test loading and merging YAML files from disk."""
    base_file = tmp_path / "base.yaml"
    override_file = tmp_path / "override.yaml"
    base_file.write_text("a: 1\nb:\n  c: 2\n")
    override_file.write_text("b:\n  c: 99\n")

    res = load_merged_config(base_file, override_file)
    assert res["a"] == 1
    assert res["b"]["c"] == 99


def test_load_yaml_missing() -> None:
    """Test FileNotFoundError on non-existent config."""
    with pytest.raises(FileNotFoundError):
        load_yaml("configs/non_existent.yaml")
