"""Full hyperspectral cube composer and multi-date time series synthesis.

Assembles 3D float32 [B, H, W] hyperspectral cubes integrating:
- Soil background and canopy endmember spectral unmixing.
- Pixel-wise disease progression and 5-acre fungal blight hotspot.
- Topographic illumination effects from synthetic DEM.
- Cloud shadow, dead pixels, and Gaussian sensor noise.
- Ground truth masks: state (0=healthy, 1=pre-symptomatic, 2=diseased),
  continuous severity [0,1], and multi-horizon binary forecast labels (7, 14, 21 days).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

from terraspectra.core.constants import GSD_M, N_BANDS, NODATA
from terraspectra.core.schemas import PixelState
from terraspectra.synth.fields import (
    inject_disease_hotspot,
    make_dem_and_shading,
    make_farm_mask,
    make_parcels,
    make_soil_spectrum,
)
from terraspectra.synth.leaf import simulate_healthy_leaf
from terraspectra.synth.stress import (
    VISIBLE_SYMPTOM_THRESHOLD,
    apply_stress_to_spectrum,
    compute_days_to_symptoms,
    compute_severity_at_day,
)
from terraspectra.synth.wavelengths import make_valid_band_mask, make_wavelengths


@dataclass
class SyntheticScene:
    """Full assembled synthetic scene container."""

    scene_id: str
    cube: NDArray[np.float32]  # [B, H, W]
    wavelengths_nm: NDArray[np.float32]  # [B]
    state_mask: NDArray[np.uint8]  # [H, W] (0=healthy, 1=stress, 2=disease, 255=nodata)
    severity_mask: NDArray[np.float32]  # [H, W] [0, 1]
    days_to_symptoms: NDArray[np.float32]  # [H, W] (days, nan if healthy)
    forecast_7d: NDArray[np.uint8]  # [H, W] binary
    forecast_14d: NDArray[np.uint8]  # [H, W] binary
    forecast_21d: NDArray[np.uint8]  # [H, W] binary
    farm_mask: NDArray[np.bool_]  # [H, W]
    parcels: NDArray[np.int32]  # [H, W]
    dem_m: NDArray[np.float32]  # [H, W]
    hotspot_acres: float
    hotspot_center: tuple[int, int]
    metadata: dict[str, Any]


def compose_cube(
    rows: int = 128,
    cols: int = 128,
    n_bands: int = N_BANDS,
    day_in_progression: float = 14.0,
    hotspot_acres: float = 5.0,
    seed: int = 42,
    add_noise: bool = True,
    add_clouds: bool = False,
    scene_id: str = "farm_001",
) -> SyntheticScene:
    """Compose a full hyperspectral cube with 5-acre disease outbreak dynamics.

    Args:
        rows: Spatial height in pixels (default 128).
        cols: Spatial width in pixels (default 128).
        n_bands: Number of spectral bands (default 224).
        day_in_progression: Temporal day of disease incubation (day 14 = pre-symptomatic).
        hotspot_acres: Outbreak footprint area in acres (default 5.0).
        seed: Random seed for reproducibility.
        add_noise: Whether to inject sensor noise.
        add_clouds: Whether to inject cloud shadows and dead pixels.
        scene_id: Identifier string.

    Returns:
        Populated SyntheticScene instance.
    """
    rng = np.random.default_rng(seed)
    wavelengths = make_wavelengths(n_bands=n_bands)
    valid_mask = make_valid_band_mask(wavelengths)

    # 1. Spatial farm layout (approx 1,000 acres in center)
    farm_mask, farm_px = make_farm_mask(rows=rows, cols=cols, target_acres=1000.0)
    parcels = make_parcels(farm_mask)

    # 2. Disease severity field at current day
    # Day 14 peak severity reaches ~0.45-0.55 (pre-symptomatic stress)
    peak_sev = compute_severity_at_day(day=day_in_progression)
    severity_map, epicenter, calculated_acres = inject_disease_hotspot(
        shape=(rows, cols),
        farm_mask=farm_mask,
        hotspot_acres=hotspot_acres,
        max_severity=peak_sev,
        rng=rng,
    )

    # 3. Terrain and illumination
    dem, hillshade = make_dem_and_shading(shape=(rows, cols), rng=rng)

    # 4. Generate base endmember spectra
    healthy_spectrum = simulate_healthy_leaf(wavelengths, rng=rng)
    soil_spectrum = make_soil_spectrum(wavelengths)

    # Pre-allocate cube [B, H, W]
    cube = np.zeros((n_bands, rows, cols), dtype=np.float32)

    # Soil background variation
    soil_grf = rng.uniform(0.9, 1.1, size=(rows, cols)).astype(np.float32)

    # 5. Populate spectral signatures per pixel
    for r in range(rows):
        for c in range(cols):
            if not farm_mask[r, c]:
                # Non-farm background: bare soil / sparse vegetation
                base_px = soil_spectrum * soil_grf[r, c]
                cube[:, r, c] = base_px * hillshade[r, c]
            else:
                sev = float(severity_map[r, c])
                if sev < 0.05:
                    # Healthy crop canopy with ~85% cover + 15% soil
                    canopy = healthy_spectrum * rng.uniform(0.97, 1.03)
                    mix = 0.88 * canopy + 0.12 * soil_spectrum
                else:
                    # Stressed / diseased crop spectrum
                    stressed = apply_stress_to_spectrum(wavelengths, severity=sev, rng=rng)
                    mix = 0.88 * stressed + 0.12 * soil_spectrum

                cube[:, r, c] = mix * hillshade[r, c]

    # 6. Add atmospheric & sensor noise
    if add_noise:
        noise = rng.normal(0.0, 0.005, size=cube.shape).astype(np.float32)
        cube += noise

    # 7. Optional cloud shadow and dead pixels
    if add_clouds:
        # Dim a patch by 40% (cloud shadow)
        cr, cc = int(rows * 0.2), int(cols * 0.2)
        cube[:, cr : cr + 15, cc : cc + 15] *= 0.60
        # Dead detector line in band 42
        cube[42, :, :] = 0.0

    # Ensure reflectance remains non-negative
    cube = np.clip(cube, 0.001, 0.99).astype(np.float32)

    # 8. Compute ground truth label masks
    state_mask = np.full((rows, cols), 255, dtype=np.uint8)  # non-farm = 255
    state_mask[farm_mask & (severity_map < 0.20)] = PixelState.HEALTHY
    state_mask[farm_mask & (severity_map >= 0.20) & (severity_map < VISIBLE_SYMPTOM_THRESHOLD)] = (
        PixelState.PRE_SYMPTOMATIC
    )
    state_mask[farm_mask & (severity_map >= VISIBLE_SYMPTOM_THRESHOLD)] = PixelState.VISIBLY_DISEASED

    # Days to symptoms
    days_to_sym = compute_days_to_symptoms(severity_map).astype(np.float32)

    # Multi-horizon forecast labels: will this pixel show visible symptoms within H days?
    # Visible when days_to_symptoms <= H (and pixel is in farm)
    forecast_7d = np.where(
        farm_mask & (~np.isnan(days_to_sym)) & (days_to_sym <= 7.0), 1, 0
    ).astype(np.uint8)
    forecast_14d = np.where(
        farm_mask & (~np.isnan(days_to_sym)) & (days_to_sym <= 14.0), 1, 0
    ).astype(np.uint8)
    forecast_21d = np.where(
        farm_mask & (~np.isnan(days_to_sym)) & (days_to_sym <= 21.0), 1, 0
    ).astype(np.uint8)

    # 9. Metadata sidecar dictionary
    metadata = {
        "scene_id": scene_id,
        "format": "HDF5/GeoTIFF",
        "shape": [n_bands, rows, cols],
        "gsd_m": GSD_M,
        "crs": "EPSG:32643",
        "day_in_progression": day_in_progression,
        "target_hotspot_acres": hotspot_acres,
        "calculated_hotspot_acres": round(calculated_acres, 2),
        "epicenter_rc": list(epicenter),
        "farm_acres": round(float(farm_px * (GSD_M**2) / 4046.8564), 2),
        "seed": seed,
    }

    return SyntheticScene(
        scene_id=scene_id,
        cube=cube,
        wavelengths_nm=wavelengths,
        state_mask=state_mask,
        severity_mask=severity_map,
        days_to_symptoms=days_to_sym,
        forecast_7d=forecast_7d,
        forecast_14d=forecast_14d,
        forecast_21d=forecast_21d,
        farm_mask=farm_mask,
        parcels=parcels,
        dem_m=dem,
        hotspot_acres=calculated_acres,
        hotspot_center=epicenter,
        metadata=metadata,
    )


def generate_time_series(
    scene_id: str = "farm_001",
    dates: list[float] | None = None,
    hotspot_acres: float = 5.0,
    seed: int = 42,
    rows: int = 128,
    cols: int = 128,
) -> list[SyntheticScene]:
    """Generate multi-temporal time series of hyperspectral cubes (e.g. 4 revisit dates).

    Simulates temporal progression from day 0 (completely healthy), day 7 (early infection),
    day 14 (pre-symptomatic stress - target forecast window), to day 21 (visible symptoms emerge).

    Args:
        scene_id: Base identifier.
        dates: List of disease incubation days to simulate.
        hotspot_acres: Footprint of disease cluster.
        seed: Random seed.
        rows: Height.
        cols: Width.

    Returns:
        List of SyntheticScene objects.
    """
    if dates is None:
        dates = [0.0, 7.0, 14.0, 21.0]

    series: list[SyntheticScene] = []
    for d in dates:
        t_id = f"{scene_id}_d{int(d):02d}"
        scene = compose_cube(
            rows=rows,
            cols=cols,
            day_in_progression=d,
            hotspot_acres=hotspot_acres,
            seed=seed,
            scene_id=t_id,
        )
        series.append(scene)
    return series

