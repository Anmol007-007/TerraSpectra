"""Synthetic data generation pipeline exports."""

from terraspectra.synth.cube import SyntheticScene, compose_cube, generate_time_series
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

__all__ = [
    "SyntheticScene",
    "compose_cube",
    "generate_time_series",
    "simulate_healthy_leaf",
    "apply_stress_to_spectrum",
    "compute_severity_at_day",
    "compute_days_to_symptoms",
    "make_farm_mask",
    "make_parcels",
    "make_soil_spectrum",
    "inject_disease_hotspot",
    "make_dem_and_shading",
    "make_wavelengths",
    "make_valid_band_mask",
    "VISIBLE_SYMPTOM_THRESHOLD",
]
