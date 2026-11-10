"""Custom exception hierarchy for TerraSpectra."""

from __future__ import annotations


class TerraSpectraError(Exception):
    """Base exception for all TerraSpectra errors."""


class DataError(TerraSpectraError):
    """Raised when data loading or validation fails."""


class ShapeError(DataError):
    """Raised when a tensor or array has an unexpected shape."""


class ModelError(TerraSpectraError):
    """Raised when model loading or inference fails."""


class APIError(TerraSpectraError):
    """Raised for API-layer errors."""


class SceneNotFoundError(APIError):
    """Raised when a requested scene is not in the catalog."""


class JobNotFoundError(APIError):
    """Raised when a requested job ID does not exist."""
