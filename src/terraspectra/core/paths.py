"""Filesystem path helpers for data pipelines and artifact storage."""

from __future__ import annotations

from pathlib import Path

from terraspectra.core.settings import settings


def ensure_dir(path: Path | str) -> Path:
    """Create directory and parents if they do not exist.

    Args:
        path: Path to ensure.

    Returns:
        Resolved Path instance.
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_raw_cube_path(scene_id: str, extension: str = ".tif") -> Path:
    """Return destination path for raw hyperspectral cube."""
    return ensure_dir(settings.raw_data_dir) / f"{scene_id}{extension}"


def get_interim_cube_path(scene_id: str, suffix: str = "_cleaned.h5") -> Path:
    """Return destination path for cleaned/intermediate cube."""
    return ensure_dir(settings.interim_data_dir) / f"{scene_id}{suffix}"


def get_processed_cube_path(scene_id: str, suffix: str = "_pca32.h5") -> Path:
    """Return destination path for analysis-ready PCA reduced cube."""
    return ensure_dir(settings.processed_data_dir) / f"{scene_id}{suffix}"


def get_model_checkpoint_path(model_version: str, filename: str = "best.pt") -> Path:
    """Return checkpoint filepath inside models_store."""
    version_dir = ensure_dir(settings.models_dir / model_version)
    return version_dir / filename
