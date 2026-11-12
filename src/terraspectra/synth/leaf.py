"""Physical leaf reflectance model for synthetic hyperspectral data.

Simulates healthy vegetation reflectance profiles across 400-2500 nm using
Gaussian absorption bands, red-edge sigmoid transitions, NIR scattering
plateau, and leaf water absorption features.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from terraspectra.synth.wavelengths import make_valid_band_mask, make_wavelengths


def gaussian_feature(
    wavelengths: NDArray[np.float32],
    center_nm: float,
    width_nm: float,
    depth: float,
) -> NDArray[np.float32]:
    """Compute an inverted Gaussian absorption feature.

    Args:
        wavelengths: 1-D array of wavelengths in nm.
        center_nm: Center wavelength of absorption in nm.
        width_nm: Gaussian standard deviation (spread) in nm.
        depth: Peak absorption depth fraction (0 to 1).

    Returns:
        1-D float32 array of absorption multipliers (<= 1.0).
    """
    arg = -0.5 * ((wavelengths - center_nm) / width_nm) ** 2
    return (1.0 - depth * np.exp(arg)).astype(np.float32)


def red_edge_transition(
    wavelengths: NDArray[np.float32],
    inflection_nm: float = 710.0,
    slope: float = 0.08,
    vis_level: float = 0.05,
    nir_level: float = 0.50,
) -> NDArray[np.float32]:
    """Model the steep red-edge reflectance transition between 680-750 nm.

    Args:
        wavelengths: 1-D array of wavelengths in nm.
        inflection_nm: Red-edge inflection point (standard ~710 nm).
        slope: Steepness parameter of the logistic sigmoid.
        vis_level: Baseline visible red reflectance.
        nir_level: Plateau NIR reflectance.

    Returns:
        1-D float32 array of base sigmoidal reflectance.
    """
    z = slope * (wavelengths - inflection_nm)
    # Clip z to prevent float overflow
    z_clipped = np.clip(z, -30.0, 30.0)
    sigmoid = 1.0 / (1.0 + np.exp(-z_clipped))
    return (vis_level + (nir_level - vis_level) * sigmoid).astype(np.float32)


def leaf_water_absorption(
    wavelengths: NDArray[np.float32],
    water_factor: float = 1.0,
) -> NDArray[np.float32]:
    """Compute leaf liquid water absorption across 970, 1200, 1450, 1940 nm.

    Args:
        wavelengths: 1-D array of wavelengths in nm.
        water_factor: Multiplier for water content (1.0 = normal hydrated).

    Returns:
        1-D float32 array of water transmission multipliers.
    """
    water_features = [
        (970.0, 40.0, 0.12 * water_factor),
        (1200.0, 50.0, 0.20 * water_factor),
        (1450.0, 70.0, 0.65 * water_factor),
        (1940.0, 80.0, 0.70 * water_factor),
    ]
    mult = np.ones_like(wavelengths, dtype=np.float32)
    for center, width, depth in water_features:
        clipped_depth = min(0.95, max(0.0, depth))
        mult *= gaussian_feature(wavelengths, center, width, clipped_depth)
    return mult.astype(np.float32)


def swir_dry_matter_slope(
    wavelengths: NDArray[np.float32],
    slope: float = -0.00008,
) -> NDArray[np.float32]:
    """Model dry-matter (cellulose, lignin, starch) slope in SWIR (1500-2500 nm).

    Args:
        wavelengths: 1-D array of wavelengths in nm.
        slope: Linear slope per nm above 1400 nm.

    Returns:
        1-D float32 additive adjustment array.
    """
    offset = np.zeros_like(wavelengths, dtype=np.float32)
    swir_mask = wavelengths > 1400.0
    offset[swir_mask] = slope * (wavelengths[swir_mask] - 1400.0)
    return offset.astype(np.float32)


def sensor_noise(
    wavelengths: NDArray[np.float32],
    base_snr: float = 200.0,
    swir_noise_multiplier: float = 2.0,
    rng: np.random.Generator | None = None,
) -> NDArray[np.float32]:
    """Generate wavelength-dependent sensor noise (higher noise in SWIR).

    Args:
        wavelengths: 1-D array of wavelengths in nm.
        base_snr: Base signal-to-noise ratio in VNIR.
        swir_noise_multiplier: Factor increasing noise in SWIR bands.
        rng: Optional NumPy random Generator.

    Returns:
        1-D float32 array of additive noise values.
    """
    if rng is None:
        rng = np.random.default_rng()
    sigma = 1.0 / base_snr
    noise_sigma = np.full_like(wavelengths, sigma, dtype=np.float32)
    swir_mask = wavelengths > 1000.0
    noise_sigma[swir_mask] *= swir_noise_multiplier
    return rng.normal(0.0, noise_sigma).astype(np.float32)


def simulate_healthy_leaf(
    wavelengths: NDArray[np.float32],
    water_factor: float = 1.0,
    chlorophyll_factor: float = 1.0,
    add_noise: bool = False,
    rng: np.random.Generator | None = None,
) -> NDArray[np.float32]:
    """Simulate physically-realistic healthy green vegetation reflectance spectrum.

    Features modeled:
    - Chlorophyll a/b absorption: 450 nm (blue) and 670 nm (red).
    - Carotenoid absorption: ~480-500 nm.
    - Green reflectance peak: ~550 nm (~0.12).
    - Red-edge sigmoid rise: 680-750 nm (inflection ~710 nm).
    - NIR scattering plateau: 750-1300 nm (~0.45-0.55).
    - Liquid water absorption: 970, 1200, 1450, 1940 nm.
    - SWIR dry-matter features: 1500-2400 nm.

    Args:
        wavelengths: 1-D array of wavelengths in nm.
        water_factor: Leaf water content scaling (1.0 = healthy).
        chlorophyll_factor: Chlorophyll content scaling (1.0 = healthy).
        add_noise: Whether to inject sensor noise.
        rng: Optional NumPy random Generator.

    Returns:
        1-D float32 array of surface reflectance in [0.0, 1.0].
    """
    # 1. Base shape from red edge sigmoid transition
    r = red_edge_transition(wavelengths, inflection_nm=710.0, vis_level=0.06, nir_level=0.52)

    # 2. Green reflectance peak at 550 nm (prominent in healthy crops)
    green_peak = 0.08 * np.exp(-0.5 * ((wavelengths - 550.0) / 25.0) ** 2)
    r += green_peak.astype(np.float32)

    # 3. Chlorophyll absorption in blue (450 nm) and red (670 nm)
    chl_blue = gaussian_feature(wavelengths, 450.0, 30.0, 0.40 * chlorophyll_factor)
    chl_red = gaussian_feature(wavelengths, 670.0, 20.0, 0.50 * chlorophyll_factor)
    r *= (chl_blue * chl_red).astype(np.float32)

    # 4. Carotenoid absorption (480-500 nm)
    carotenoid = gaussian_feature(wavelengths, 490.0, 25.0, 0.20 * chlorophyll_factor)
    r *= carotenoid.astype(np.float32)

    # 5. Liquid water absorption in NIR and SWIR
    water = leaf_water_absorption(wavelengths, water_factor=water_factor)
    r *= water

    # 6. SWIR dry matter adjustment
    r += swir_dry_matter_slope(wavelengths)

    # 7. Sensor noise
    if add_noise:
        r += sensor_noise(wavelengths, rng=rng)

    # Physically bounded reflectance in [0.0, 1.0]
    return np.clip(r, 0.005, 0.95).astype(np.float32)

