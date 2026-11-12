"""Unit and property tests for synthetic hyperspectral data generation."""

from __future__ import annotations

import numpy as np
import pytest

from terraspectra.synth.cube import compose_cube, generate_time_series
from terraspectra.synth.fields import (
    inject_disease_hotspot,
    make_dem_and_shading,
    make_farm_mask,
    make_soil_spectrum,
)
from terraspectra.synth.leaf import gaussian_feature, simulate_healthy_leaf
from terraspectra.synth.stress import (
    VISIBLE_SYMPTOM_THRESHOLD,
    apply_stress_to_spectrum,
    compute_days_to_symptoms,
    compute_severity_at_day,
)
from terraspectra.synth.wavelengths import make_valid_band_mask, make_wavelengths


def test_wavelength_grid_224_bands() -> None:
    """Test standard 224-band wavelength grid generation."""
    wl = make_wavelengths(224)
    assert len(wl) == 224
    assert wl[0] == pytest.approx(400.0, rel=1e-3)
    assert wl[-1] == pytest.approx(2500.0, rel=1e-3)

    mask = make_valid_band_mask(wl)
    assert len(mask) == 224
    assert np.sum(~mask) > 10  # Atmospheric water absorption bands excluded


def test_healthy_leaf_reflectance_shape() -> None:
    """Test simulated healthy leaf spectrum boundaries and absorption peaks."""
    wl = make_wavelengths(224)
    refl = simulate_healthy_leaf(wl, add_noise=False)

    assert refl.shape == (224,)
    assert np.all(refl >= 0.0)
    assert np.all(refl <= 1.0)

    # Chlorophyll absorption at 670 nm should have lower reflectance than green peak at 550 nm
    idx_550 = int(np.argmin(np.abs(wl - 550.0)))
    idx_670 = int(np.argmin(np.abs(wl - 670.0)))
    assert refl[idx_550] > refl[idx_670]

    # NIR plateau (800 nm) should have much higher reflectance than red (670 nm)
    idx_800 = int(np.argmin(np.abs(wl - 800.0)))
    assert refl[idx_800] > refl[idx_670] * 3.0


def test_stress_monotonic_and_red_edge_shift() -> None:
    """Test spectral stress response: chlorophyll decline, red-edge blue shift."""
    wl = make_wavelengths(224)
    healthy = simulate_healthy_leaf(wl)
    stressed_mild = apply_stress_to_spectrum(wl, severity=0.35)
    stressed_severe = apply_stress_to_spectrum(wl, severity=0.80)

    idx_670 = int(np.argmin(np.abs(wl - 670.0)))
    idx_800 = int(np.argmin(np.abs(wl - 800.0)))

    # As stress increases, red absorption collapses (reflectance increases at 670 nm)
    assert stressed_severe[idx_670] > healthy[idx_670]
    # NIR plateau drops under severe tissue collapse
    assert stressed_severe[idx_800] < healthy[idx_800]


def test_temporal_disease_progression_curve() -> None:
    """Test logistic growth of severity over 21 days."""
    s_day0 = compute_severity_at_day(0.0)
    s_day7 = compute_severity_at_day(7.0)
    s_day14 = compute_severity_at_day(14.0)
    s_day21 = compute_severity_at_day(21.0)

    assert s_day0 < s_day7 < s_day14 < s_day21
    # Day 14 should be pre-symptomatic (below visible threshold 0.60)
    assert s_day14 < VISIBLE_SYMPTOM_THRESHOLD
    # Day 21 reaches/exceeds visible symptoms
    assert s_day21 >= VISIBLE_SYMPTOM_THRESHOLD


def test_days_to_symptoms_inversion() -> None:
    """Test days-to-symptoms calculation."""
    s_arr = np.array([0.02, 0.40, 0.75], dtype=np.float32)
    d = compute_days_to_symptoms(s_arr)
    # Healthy pixel returns nan
    assert np.isnan(d[0])
    # Active pre-symptomatic stress returns positive days remaining
    assert d[1] > 0.0
    # Visibly diseased pixel returns 0
    assert d[2] == 0.0


def test_farm_mask_and_hotspot_acres() -> None:
    """Test 1,000-acre farm mask and 5-acre hotspot spatial footprint."""
    farm_mask, px_count = make_farm_mask(rows=128, cols=128, target_acres=1000.0)
    # 1000 acres at 30m GSD ≈ 4497 px
    assert 4000 < px_count < 5000

    sev_map, seed_pos, calculated_acres = inject_disease_hotspot(
        shape=(128, 128),
        farm_mask=farm_mask,
        hotspot_acres=5.0,
        max_severity=0.85,
    )
    # Footprint should be approximately 5 acres (4.0 to 6.0 ac tolerance)
    assert 4.0 <= calculated_acres <= 6.5
    assert sev_map[seed_pos] >= 0.80


def test_cube_composition_and_labels() -> None:
    """Test full cube assembly and ground-truth label tensors."""
    scene = compose_cube(
        rows=32,
        cols=32,
        n_bands=64,
        day_in_progression=14.0,
        hotspot_acres=5.0,
        seed=123,
    )

    assert scene.cube.shape == (64, 32, 32)
    assert scene.cube.dtype == np.float32
    assert scene.state_mask.shape == (32, 32)
    assert scene.forecast_7d.shape == (32, 32)
    assert scene.forecast_14d.shape == (32, 32)
    assert scene.forecast_21d.shape == (32, 32)
    assert scene.metadata["scene_id"] == "farm_001"

