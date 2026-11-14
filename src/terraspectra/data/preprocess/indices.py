"""Diagnostic vegetation indices and biochemical spectral ratios."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from terraspectra.core.constants import (
    CIRE_710_NM,
    CIRE_780_NM,
    NDVI_NIR_NM,
    NDVI_RED_NM,
    NDWI_860_NM,
    NDWI_1240_NM,
    PRI_531_NM,
    PRI_570_NM,
    RED_EDGE_MAX_NM,
    RED_EDGE_MIN_NM,
)


def _find_nearest_band_idx(wavelengths_nm: NDArray[np.float32], target_nm: float) -> int:
    return int(np.argmin(np.abs(wavelengths_nm - target_nm)))


def compute_ndvi(
    cube: NDArray[np.float32],  # [B, H, W]
    wavelengths_nm: NDArray[np.float32],
) -> NDArray[np.float32]:
    """Normalized Difference Vegetation Index: (R800 - R670) / (R800 + R670)."""
    i_nir = _find_nearest_band_idx(wavelengths_nm, NDVI_NIR_NM)
    i_red = _find_nearest_band_idx(wavelengths_nm, NDVI_RED_NM)
    r_nir = cube[i_nir]
    r_red = cube[i_red]
    denom = r_nir + r_red + 1e-6
    return np.clip((r_nir - r_red) / denom, -1.0, 1.0).astype(np.float32)


def compute_pri(
    cube: NDArray[np.float32],
    wavelengths_nm: NDArray[np.float32],
) -> NDArray[np.float32]:
    """Photochemical Reflectance Index: (R531 - R570) / (R531 + R570)."""
    i_531 = _find_nearest_band_idx(wavelengths_nm, PRI_531_NM)
    i_570 = _find_nearest_band_idx(wavelengths_nm, PRI_570_NM)
    r_531 = cube[i_531]
    r_570 = cube[i_570]
    denom = r_531 + r_570 + 1e-6
    return np.clip((r_531 - r_570) / denom, -1.0, 1.0).astype(np.float32)


def compute_ndwi(
    cube: NDArray[np.float32],
    wavelengths_nm: NDArray[np.float32],
) -> NDArray[np.float32]:
    """Normalized Difference Water Index: (R860 - R1240) / (R860 + R1240)."""
    i_860 = _find_nearest_band_idx(wavelengths_nm, NDWI_860_NM)
    i_1240 = _find_nearest_band_idx(wavelengths_nm, NDWI_1240_NM)
    r_860 = cube[i_860]
    r_1240 = cube[i_1240]
    denom = r_860 + r_1240 + 1e-6
    return np.clip((r_860 - r_1240) / denom, -1.0, 1.0).astype(np.float32)


def compute_cire(
    cube: NDArray[np.float32],
    wavelengths_nm: NDArray[np.float32],
) -> NDArray[np.float32]:
    """Chlorophyll Index Red-Edge: (R780 / R710) - 1."""
    i_780 = _find_nearest_band_idx(wavelengths_nm, CIRE_780_NM)
    i_710 = _find_nearest_band_idx(wavelengths_nm, CIRE_710_NM)
    r_780 = cube[i_780]
    r_710 = np.maximum(1e-4, cube[i_710])
    return ((r_780 / r_710) - 1.0).astype(np.float32)


def compute_red_edge_position(
    cube: NDArray[np.float32],
    wavelengths_nm: NDArray[np.float32],
) -> NDArray[np.float32]:
    """Red Edge Position (REP): Wavelength of maximum 1st spectral derivative in 680-750 nm."""
    mask = (wavelengths_nm >= RED_EDGE_MIN_NM) & (wavelengths_nm <= RED_EDGE_MAX_NM)
    sub_wl = wavelengths_nm[mask]
    sub_cube = cube[mask]  # [B_sub, H, W]

    if len(sub_wl) < 3:
        return np.full(cube.shape[1:], 710.0, dtype=np.float32)

    # First derivative along band axis
    diff = np.gradient(sub_cube, sub_wl, axis=0)  # [B_sub, H, W]
    max_idx = np.argmax(diff, axis=0)  # [H, W]
    rep = sub_wl[max_idx]
    return rep.astype(np.float32)


def compute_mcari(
    cube: NDArray[np.float32],
    wavelengths_nm: NDArray[np.float32],
) -> NDArray[np.float32]:
    """Modified Chlorophyll Absorption in Reflectance Index:
    ((R700 - R670) - 0.2 * (R700 - R550)) * (R700 / R670).
    """
    i_700 = _find_nearest_band_idx(wavelengths_nm, 700.0)
    i_670 = _find_nearest_band_idx(wavelengths_nm, 670.0)
    i_550 = _find_nearest_band_idx(wavelengths_nm, 550.0)

    r_700 = cube[i_700]
    r_670 = np.maximum(1e-4, cube[i_670])
    r_550 = cube[i_550]

    mcari = ((r_700 - r_670) - 0.2 * (r_700 - r_550)) * (r_700 / r_670)
    return mcari.astype(np.float32)


def build_index_stack(
    cube: NDArray[np.float32],
    wavelengths_nm: NDArray[np.float32],
) -> tuple[NDArray[np.float32], list[str]]:
    """Compute and stack all 6 key agricultural diagnostic indices.

    Returns:
        (stack_3d [6, H, W], index_names).
    """
    ndvi = compute_ndvi(cube, wavelengths_nm)
    pri = compute_pri(cube, wavelengths_nm)
    ndwi = compute_ndwi(cube, wavelengths_nm)
    cire = compute_cire(cube, wavelengths_nm)
    rep = compute_red_edge_position(cube, wavelengths_nm)
    mcari = compute_mcari(cube, wavelengths_nm)

    stack = np.stack([ndvi, pri, ndwi, cire, rep, mcari], axis=0)
    names = ["NDVI", "PRI", "NDWI", "CIre", "REP", "MCARI"]
    return stack.astype(np.float32), names

