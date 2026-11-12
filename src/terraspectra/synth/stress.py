"""Crop disease progression and spectral stress dynamics model.

Implements the physical transformation of hyperspectral reflectance under
pre-symptomatic stress and visible fungal blight disease progression:
- Chlorophyll breakdown and red-edge blue shift (~ -8 nm * severity).
- Photochemical Reflectance Index (PRI, 531/570 nm) decline.
- Leaf cellular dehydration and water band flattening.
- SWIR dry-matter reflectance increase (+0.04 * severity).
- Logistic temporal disease progression over a 21-day incubation window.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from terraspectra.synth.leaf import (
    gaussian_feature,
    leaf_water_absorption,
    red_edge_transition,
    sensor_noise,
    swir_dry_matter_slope,
)

VISIBLE_SYMPTOM_THRESHOLD: float = 0.60
FORECAST_INCUBATION_DAYS: int = 21


def compute_severity_at_day(
    day: float,
    incubation_days: int = FORECAST_INCUBATION_DAYS,
    max_severity: float = 1.0,
    growth_rate: float = 0.35,
) -> float:
    """Compute disease severity along a logistic temporal progression curve.

    S(t) starts near 0 at t=0, reaches pre-symptomatic stress (0.2-0.5) during
    days 7-14, and crosses visible threshold (0.60) at day ~21.

    Args:
        day: Current day relative to initial fungal spore inoculation (0 to 30).
        incubation_days: Target day when visible symptoms emerge.
        max_severity: Asymptotic maximum severity (default 1.0).
        growth_rate: Logistic steepness parameter.

    Returns:
        Severity float value in [0.0, 1.0].
    """
    # Midpoint of the logistic curve set near day 18-20 so threshold 0.60 is crossed at day 21
    t0 = incubation_days - 2.5
    z = growth_rate * (day - t0)
    z_clipped = np.clip(z, -30.0, 30.0)
    sev = max_severity / (1.0 + np.exp(-z_clipped))
    return float(np.clip(sev, 0.0, 1.0))


def compute_days_to_symptoms(
    severity: float | NDArray[np.float32],
    growth_rate: float = 0.35,
    threshold: float = VISIBLE_SYMPTOM_THRESHOLD,
    incubation_days: int = FORECAST_INCUBATION_DAYS,
) -> float | NDArray[np.float32]:
    """Invert the logistic curve to compute remaining days until visible symptoms.

    Returns NaN for completely healthy pixels (severity < 0.05).
    Returns 0.0 for pixels already showing visible disease (severity >= threshold).

    Args:
        severity: Current severity (scalar or array).
        growth_rate: Logistic steepness parameter.
        threshold: Severity threshold for visible symptoms (0.60).
        incubation_days: Benchmark incubation duration in days.

    Returns:
        Estimated days to visible symptoms.
    """
    is_array = isinstance(severity, np.ndarray)
    s = np.asarray(severity, dtype=np.float32)

    t0 = incubation_days - 2.5
    # For s in (0.01, threshold):
    # s = 1 / (1 + exp(-k*(t - t0))) -> t = t0 - ln(1/s - 1)/k
    # days_to_symptoms = 21 - t
    out = np.full_like(s, np.nan, dtype=np.float32)

    active_mask = (s >= 0.05) & (s < threshold)
    diseased_mask = s >= threshold

    out[diseased_mask] = 0.0

    if np.any(active_mask):
        s_act = np.clip(s[active_mask], 0.01, 0.99)
        t_est = t0 - (np.log(1.0 / s_act - 1.0) / growth_rate)
        rem = np.maximum(0.0, float(incubation_days) - t_est)
        out[active_mask] = rem.astype(np.float32)

    return out if is_array else float(out.item())


def apply_stress_to_spectrum(
    wavelengths: NDArray[np.float32],
    severity: float,
    add_noise: bool = False,
    rng: np.random.Generator | None = None,
) -> NDArray[np.float32]:
    """Transform baseline healthy vegetation spectrum as a function of disease severity.

    Physical shifts:
    1. Chlorophyll decline: 1 - 0.5 * s.
    2. Red-edge inflection shift: 710 nm -> 710 - (8.0 * s) nm (blue shift).
    3. PRI decrease: Xanthophyll epoxidation shifts 531 nm reflectance down relative to 570 nm.
    4. Cellular dehydration: water absorption depth scales by 1 - 0.65 * s.
    5. Structural breakdown: SWIR reflectance increases by +0.05 * s.

    Args:
        wavelengths: 1-D array of wavelengths in nm.
        severity: Disease severity fraction in [0.0, 1.0].
        add_noise: Whether to add sensor noise.
        rng: Optional NumPy random Generator.

    Returns:
        1-D float32 array of stressed vegetation reflectance.
    """
    s = float(np.clip(severity, 0.0, 1.0))

    # 1. Red-edge shift: shifts toward shorter wavelengths (blue shift)
    inflection = 710.0 - 8.0 * s
    r = red_edge_transition(
        wavelengths,
        inflection_nm=inflection,
        vis_level=0.06 + 0.08 * s,  # Visible red brightens as chlorophyll fades
        nir_level=0.52 - 0.15 * s,  # NIR plateau drops as spongy mesophyll collapses
    )

    # 2. Green reflectance peak (fades into chlorosis yellowing)
    green_peak = (0.08 - 0.03 * s) * np.exp(-0.5 * ((wavelengths - 550.0) / 25.0) ** 2)
    # Chlorosis yellow reflectance increase near 580-620 nm
    yellow_increase = (0.07 * s) * np.exp(-0.5 * ((wavelengths - 590.0) / 35.0) ** 2)
    r += (green_peak + yellow_increase).astype(np.float32)

    # 3. Chlorophyll absorption reduced as severity increases
    chl_scale = max(0.05, 1.0 - 0.55 * s)
    chl_blue = gaussian_feature(wavelengths, 450.0, 30.0, 0.40 * chl_scale)
    chl_red = gaussian_feature(wavelengths, 670.0, 20.0, 0.50 * chl_scale)
    r *= (chl_blue * chl_red).astype(np.float32)

    # 4. Photochemical Reflectance Index (PRI) stress signal at 531 nm
    # PRI = (R531 - R570) / (R531 + R570) declines under stress
    pri_attenuation = gaussian_feature(wavelengths, 531.0, 10.0, 0.10 * s)
    r *= pri_attenuation.astype(np.float32)

    # 5. Leaf water loss (features at 970, 1200, 1450, 1940 nm become shallower)
    water_factor = max(0.15, 1.0 - 0.70 * s)
    water = leaf_water_absorption(wavelengths, water_factor=water_factor)
    r *= water

    # 6. SWIR reflectance increase (structural breakdown & dry matter exposure)
    r += swir_dry_matter_slope(wavelengths)
    swir_mask = wavelengths > 1300.0
    r[swir_mask] += np.float32(0.05 * s)

    # 7. Optional sensor noise
    if add_noise:
        r += sensor_noise(wavelengths, rng=rng)

    return np.clip(r, 0.005, 0.95).astype(np.float32)

