"""Custom exception hierarchy for TerraSpectra."""

from __future__ import annotations


class TerraSpectraError(Exception):
    """Base exception for all TerraSpectra errors."""


class DataError(TerraSpectraError):
    """Raised when data loading, reading, or format validation fails."""


class ShapeError(DataError):
    """Raised when a hyperspectral cube or patch has unexpected tensor dimensions."""


class BandMismatchError(DataError):
    """Raised when cube spectral channels do not match model expectation."""


class ModelError(TerraSpectraError):
    """Raised when model architecture, weights loading, or inference fails."""


class TilingError(TerraSpectraError):
    """Raised when spatial tiling or Hann window stitching encounters dimension mismatch."""


class OutOfMemoryError(ModelError):
    """Raised when GPU VRAM or host memory budget is exhausted during batch inference."""


class APIError(TerraSpectraError):
    """Raised for API-layer service request errors."""


class SceneNotFoundError(APIError):
    """Raised when a requested scene is not present in the catalog."""


class JobNotFoundError(APIError):
    """Raised when a requested inference job ID does not exist."""
