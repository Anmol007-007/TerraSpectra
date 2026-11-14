"""Spectral cube cleaning, noise mitigation, smoothing, and QA diagnostics."""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.signal import savgol_filter

from terraspectra.core.constants import BAD_BAND_RANGES, NODATA


def drop_bad_bands(
    cube: NDArray[np.float32],  # [B, H, W]
    wavelengths_nm: NDArray[np.float32],  # [B]
    bad_ranges: tuple[tuple[float, float], ...] = BAD_BAND_RANGES,
    nan_threshold_ratio: float = 0.20,
) -> tuple[NDArray[np.float32], NDArray[np.float32], NDArray[np.bool_]]:
    """Drop water vapour and high-noise spectral bands from the cube.

    Args:
        cube: 3D float32 array [B, H, W].
        wavelengths_nm: 1-D float32 array of band centers.
        bad_ranges: Tuple of (lo_nm, hi_nm) absorption bands to filter out.
        nan_threshold_ratio: Maximum allowable fraction of NaN/nodata pixels in a band.

    Returns:
        (filtered_cube, filtered_wavelengths, valid_mask).
    """
    b, h, w = cube.shape
    total_px = h * w
    valid_mask = np.ones(b, dtype=bool)

    # 1. Filter out atmospheric water vapour bands
    for lo, hi in bad_ranges:
        valid_mask &= ~((wavelengths_nm >= lo) & (wavelengths_nm <= hi))

    # 2. Filter out bands with excessive NaN or NODATA values
    for band_idx in range(b):
        if not valid_mask[band_idx]:
            continue
        band_slice = cube[band_idx]
        bad_px = np.isnan(band_slice) | np.isinf(band_slice) | (band_slice == NODATA)
        if np.sum(bad_px) / total_px > nan_threshold_ratio:
            valid_mask[band_idx] = False

    return cube[valid_mask], wavelengths_nm[valid_mask], valid_mask


def clean_nan_and_inf(
    cube: NDArray[np.float32],
    fill_value: float = 0.0,
) -> tuple[NDArray[np.float32], int]:
    """Replace NaN, -inf, +inf, and NODATA pixels with fill_value or spectral interpolation.

    Returns:
        (cleaned_cube, num_replaced_pixels).
    """
    cleaned = cube.copy()
    bad_mask = np.isnan(cleaned) | np.isinf(cleaned) | (cleaned == NODATA)
    num_bad = int(np.sum(bad_mask))
    if num_bad > 0:
        cleaned[bad_mask] = fill_value
    return cleaned, num_bad


def remove_spectral_spikes(
    cube: NDArray[np.float32],  # [B, H, W]
    z_threshold: float = 3.5,
) -> NDArray[np.float32]:
    """Detect and smooth isolated detector noise spikes along the spectral dimension."""
    b, h, w = cube.shape
    if b < 5:
        return cube

    # Compute difference from 3-point moving median along spectral axis
    from scipy.ndimage import median_filter

    filtered = cube.copy()
    # Apply median filter along band axis (axis=0)
    spectral_med = median_filter(filtered, size=(3, 1, 1))
    diff = np.abs(filtered - spectral_med)

    std_per_band = np.std(filtered, axis=(1, 2), keepdims=True) + 1e-6
    spike_mask = diff > (z_threshold * std_per_band)

    filtered[spike_mask] = spectral_med[spike_mask]
    return filtered


def smooth_savgol(
    cube: NDArray[np.float32],  # [B, H, W]
    window_length: int = 9,
    polyorder: int = 2,
) -> NDArray[np.float32]:
    """Apply Savitzky-Golay polynomial smoothing filter along the spectral dimension (axis=0)."""
    b = cube.shape[0]
    # Window length must be odd and <= b
    wl = min(window_length, b if b % 2 != 0 else b - 1)
    if wl <= polyorder:
        return cube

    return savgol_filter(cube, window_length=wl, polyorder=polyorder, axis=0).astype(np.float32)


def clip_reflectance(
    cube: NDArray[np.float32],
    min_val: float = 0.0,
    max_val: float = 1.0,
) -> NDArray[np.float32]:
    """Ensure physically realistic surface reflectance bounded in [0.0, 1.0]."""
    return np.clip(cube, min_val, max_val).astype(np.float32)


def generate_qa_report(
    original_cube: NDArray[np.float32],
    cleaned_cube: NDArray[np.float32],
    valid_mask: NDArray[np.bool_],
) -> dict[str, Any]:
    """Generate quality assurance diagnostics summary."""
    orig_nan = int(np.sum(np.isnan(original_cube) | (original_cube == NODATA)))
    return {
        "original_bands": int(original_cube.shape[0]),
        "clean_bands": int(cleaned_cube.shape[0]),
        "dropped_bands": int(np.sum(~valid_mask)),
        "nan_nodata_pixels_repaired": orig_nan,
        "mean_reflectance": float(np.mean(cleaned_cube)),
        "min_reflectance": float(np.min(cleaned_cube)),
        "max_reflectance": float(np.max(cleaned_cube)),
    }

