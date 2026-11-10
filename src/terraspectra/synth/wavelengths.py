"""Wavelength array generation for synthetic hyperspectral cubes."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from terraspectra.core.constants import (
    BAD_BAND_RANGES,
    N_BANDS,
    WAVELENGTH_MAX_NM,
    WAVELENGTH_MIN_NM,
)


def make_wavelengths(
    n_bands: int = N_BANDS,
    wl_min: float = WAVELENGTH_MIN_NM,
    wl_max: float = WAVELENGTH_MAX_NM,
) -> NDArray[np.float32]:
    """Return evenly-spaced wavelength array in nanometres.

    Args:
        n_bands: Number of spectral bands.
        wl_min: Minimum wavelength in nm.
        wl_max: Maximum wavelength in nm.

    Returns:
        1-D float32 array of shape (n_bands,).
    """
    return np.linspace(wl_min, wl_max, n_bands, dtype=np.float32)


def make_valid_band_mask(
    wavelengths: NDArray[np.float32],
    bad_ranges: tuple[tuple[float, float], ...] = BAD_BAND_RANGES,
) -> NDArray[np.bool_]:
    """Return boolean mask of usable (non-water-vapour) bands.

    Args:
        wavelengths: 1-D array of wavelengths in nm.
        bad_ranges: Tuple of (lo, hi) nm pairs that are invalid.

    Returns:
        Boolean array; True = valid band.
    """
    mask = np.ones(len(wavelengths), dtype=np.bool_)
    for lo, hi in bad_ranges:
        mask &= ~((wavelengths >= lo) & (wavelengths <= hi))
    return mask
