"""Spatial field and agricultural terrain simulation.

Generates:
- 1,000-acre farm boundaries and sub-parcel partitions.
- Soil background spectral mixing.
- Gaussian Random Fields (GRF) for spatial correlation.
- Outbreak seed localization and spatial disease diffusion.
- 5-acre fungal blight risk hotspot injector (≈23 pixels at 30 m GSD).
- Topographic digital elevation model (DEM) and solar illumination shading.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from terraspectra.core.constants import GSD_M
from terraspectra.geo.area import acres_to_pixels


def make_soil_spectrum(wavelengths: NDArray[np.float32]) -> NDArray[np.float32]:
    """Generate typical bare soil / background spectral curve.

    Soil shows steadily increasing reflectance from visible to SWIR without
    a sharp red-edge step.

    Args:
        wavelengths: 1-D array of wavelengths in nm.

    Returns:
        1-D float32 reflectance array.
    """
    # Monotonic rise from ~0.10 at 400 nm to ~0.35 at 2200 nm
    base = 0.08 + 0.28 * ((wavelengths - 400.0) / 2100.0)
    # Clay absorption features at 1400, 1900, 2200 nm
    from terraspectra.synth.leaf import gaussian_feature

    soil_absorptions = (
        gaussian_feature(wavelengths, 1410.0, 40.0, 0.15)
        * gaussian_feature(wavelengths, 1920.0, 50.0, 0.20)
        * gaussian_feature(wavelengths, 2200.0, 35.0, 0.12)
    )
    return np.clip(base * soil_absorptions, 0.02, 0.85).astype(np.float32)


def make_farm_mask(
    rows: int = 128,
    cols: int = 128,
    target_acres: float = 1000.0,
    gsd_m: float = GSD_M,
) -> tuple[NDArray[np.bool_], int]:
    """Create a boolean spatial mask for a ~1,000-acre contiguous farm.

    At 30 m GSD, 1 pixel = 900 m² ≈ 0.2224 acre.
    1,000 acres ≈ 4,497 pixels (approx a 67×67 rectangular farm).

    Args:
        rows: Full scene height in pixels.
        cols: Full scene width in pixels.
        target_acres: Farm acreage to enclose.
        gsd_m: Ground sampling distance in metres.

    Returns:
        (farm_mask boolean array [rows, cols], count of farm pixels).
    """
    needed_pixels = int(round(acres_to_pixels(target_acres, gsd_m=gsd_m)))
    side = int(round(np.sqrt(needed_pixels)))

    r_start = (rows - side) // 2
    c_start = (cols - side) // 2

    mask = np.zeros((rows, cols), dtype=np.bool_)
    mask[r_start : r_start + side, c_start : c_start + side] = True

    # Adjust exact pixel count if needed to match target within 1%
    current_px = int(np.sum(mask))
    return mask, current_px


def make_parcels(
    farm_mask: NDArray[np.bool_],
    n_parcels_x: int = 4,
    n_parcels_y: int = 4,
) -> NDArray[np.int32]:
    """Partition the farm mask into rectangular agricultural parcels.

    Args:
        farm_mask: Boolean mask of the farm region.
        n_parcels_x: Horizontal parcel splits.
        n_parcels_y: Vertical parcel splits.

    Returns:
        2-D int32 array where positive integers denote parcel ID, 0 is non-farm.
    """
    rows, cols = farm_mask.shape
    parcel_grid = np.zeros((rows, cols), dtype=np.int32)

    farm_coords = np.argwhere(farm_mask)
    if farm_coords.size == 0:
        return parcel_grid

    r_min, c_min = farm_coords.min(axis=0)
    r_max, c_max = farm_coords.max(axis=0) + 1

    r_edges = np.linspace(r_min, r_max, n_parcels_y + 1, dtype=int)
    c_edges = np.linspace(c_min, c_max, n_parcels_x + 1, dtype=int)

    pid = 1
    for i in range(n_parcels_y):
        for j in range(n_parcels_x):
            r0, r1 = r_edges[i], r_edges[i + 1]
            c0, c1 = c_edges[j], c_edges[j + 1]
            sub = farm_mask[r0:r1, c0:c1]
            parcel_grid[r0:r1, c0:c1][sub] = pid
            pid += 1

    return parcel_grid


def generate_gaussian_random_field(
    shape: tuple[int, int],
    scale: float = 12.0,
    rng: np.random.Generator | None = None,
) -> NDArray[np.float32]:
    """Generate spatially correlated Gaussian Random Field (GRF) via 2D Gaussian filter.

    Args:
        shape: 2D (rows, cols) dimensions.
        scale: Spatial correlation length in pixels.
        rng: Optional NumPy random Generator.

    Returns:
        2-D float32 normalized field with mean 0 and std 1.
    """
    if rng is None:
        rng = np.random.default_rng()
    noise = rng.normal(0.0, 1.0, size=shape).astype(np.float32)

    # 2D Fourier smoothing for spatial autocorrelation
    from scipy.ndimage import gaussian_filter

    smoothed = gaussian_filter(noise, sigma=scale)
    std = float(np.std(smoothed))
    if std > 1e-6:
        smoothed = (smoothed - float(np.mean(smoothed))) / std
    return smoothed.astype(np.float32)


def inject_disease_hotspot(
    shape: tuple[int, int],
    farm_mask: NDArray[np.bool_],
    hotspot_acres: float = 5.0,
    max_severity: float = 0.85,
    seed_pos: tuple[int, int] | None = None,
    gsd_m: float = GSD_M,
    rng: np.random.Generator | None = None,
) -> tuple[NDArray[np.float32], tuple[int, int], float]:
    """Inject a spatially diffused 5-acre fungal blight risk hotspot.

    At 30 m GSD, 5 acres ≈ 22.48 pixels. A 2D Gaussian circular plume with
    radius r ≈ 2.7 pixels achieves this 5-acre footprint above threshold 0.35.

    Args:
        shape: Scene 2D dimensions (rows, cols).
        farm_mask: Boolean mask of the farm region.
        hotspot_acres: Target area of the pre-symptomatic/disease hotspot.
        max_severity: Peak severity at the epicenter (0 to 1).
        seed_pos: Optional epicenter (row, col). If None, sampled inside farm.
        gsd_m: Ground sampling distance in metres.
        rng: Optional NumPy random Generator.

    Returns:
        (severity_field float32 [rows, cols], epicenter (r, c), calculated_acres).
    """
    if rng is None:
        rng = np.random.default_rng()

    rows, cols = shape
    if seed_pos is None:
        # Sample epicenter safely inside the farm interior
        farm_pts = np.argwhere(farm_mask)
        if farm_pts.size == 0:
            seed_pos = (rows // 2, cols // 2)
        else:
            # Pick a point near the center of the farm
            center = np.mean(farm_pts, axis=0)
            dists = np.sum((farm_pts - center) ** 2, axis=1)
            inner_candidates = farm_pts[dists < np.percentile(dists, 40)]
            choice_idx = rng.choice(len(inner_candidates))
            seed_pos = (int(inner_candidates[choice_idx, 0]), int(inner_candidates[choice_idx, 1]))

    r_grid, c_grid = np.ogrid[:rows, :cols]
    r0, c0 = seed_pos

    # 5 acres at 30m GSD: target pixel count N ≈ 22.5
    # For Gaussian S = S0 * exp(-dist^2 / (2 * sigma^2))
    # Area above stress threshold: ensure ratio > 1.05
    target_px = acres_to_pixels(hotspot_acres, gsd_m=gsd_m)
    ratio = max(1.05, max_severity / 0.30)
    sigma = float(np.sqrt(target_px / (2.0 * np.pi * np.log(ratio))))

    dist_sq = (r_grid - r0) ** 2 + (c_grid - c0) ** 2
    severity_map = max_severity * np.exp(-dist_sq / (2.0 * sigma**2))

    # Mask outside farm
    severity_map = np.where(farm_mask, severity_map, 0.0).astype(np.float32)

    # Calculate actual acreage above pre-symptomatic threshold (0.35)
    active_px = int(np.sum(severity_map >= 0.30))
    from terraspectra.geo.area import pixels_to_acres

    actual_acres = pixels_to_acres(active_px, gsd_m=gsd_m)

    return severity_map, seed_pos, actual_acres


def make_dem_and_shading(
    shape: tuple[int, int],
    elevation_range: tuple[float, float] = (150.0, 190.0),
    sun_azimuth_deg: float = 135.0,
    sun_elevation_deg: float = 45.0,
    rng: np.random.Generator | None = None,
) -> tuple[NDArray[np.float32], NDArray[np.float32]]:
    """Generate synthetic Digital Elevation Model (DEM) and solar hillshade map.

    Args:
        shape: (rows, cols) dimensions.
        elevation_range: (min_elev_m, max_elev_m).
        sun_azimuth_deg: Solar azimuth angle in degrees (clockwise from North).
        sun_elevation_deg: Solar altitude angle in degrees above horizon.
        rng: Optional NumPy random Generator.

    Returns:
        (dem float32 array in metres, hillshade illumination array 0.7 to 1.1).
    """
    grf = generate_gaussian_random_field(shape, scale=25.0, rng=rng)
    # Scale to elevation range
    elev_min, elev_max = elevation_range
    dem = elev_min + (grf - grf.min()) / (grf.max() - grf.min() + 1e-6) * (elev_max - elev_min)
    dem = dem.astype(np.float32)

    # Compute spatial gradients (slopes in X and Y)
    gy, gx = np.gradient(dem, GSD_M, GSD_M)

    # Solar unit vector
    zenith_rad = np.radians(90.0 - sun_elevation_deg)
    azimuth_rad = np.radians(sun_azimuth_deg)

    # Normal vector to surface: (-gx, -gy, 1) / norm
    norm = np.sqrt(gx**2 + gy**2 + 1.0)
    nx = -gx / norm
    ny = -gy / norm
    nz = 1.0 / norm

    # Illumination cos(theta) = n . s
    sx = np.sin(zenith_rad) * np.sin(azimuth_rad)
    sy = np.sin(zenith_rad) * np.cos(azimuth_rad)
    sz = np.cos(zenith_rad)

    cos_inc = nx * sx + ny * sy + nz * sz
    illumination = np.clip(0.85 + 0.25 * cos_inc, 0.60, 1.25).astype(np.float32)

    return dem, illumination

