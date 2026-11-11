"""Unit tests for geospatial area and pixel conversions."""

from __future__ import annotations

import pytest

from terraspectra.geo.area import (
    acres_to_m2,
    acres_to_pixels,
    m2_to_acres,
    pixels_to_acres,
    pixels_to_m2,
)


def test_m2_acres_roundtrip() -> None:
    """Test round-trip conversion between m2 and acres."""
    val = 12345.67
    assert acres_to_m2(m2_to_acres(val)) == pytest.approx(val, rel=1e-6)
    assert m2_to_acres(acres_to_m2(val)) == pytest.approx(val, rel=1e-6)


def test_5_acre_hotspot_case() -> None:
    """Test 5-acre disease risk zone calculation at 30m GSD."""
    # 5 acres ≈ 20,234.28 m²; 1 pixel = 900 m² → 20234.28 / 900 ≈ 22.48 pixels
    acres = 5.0
    m2 = acres_to_m2(acres)
    assert m2 == pytest.approx(20234.28, rel=1e-3)
    px = acres_to_pixels(acres, gsd_m=30.0)
    assert round(px) in (22, 23)
    assert pixels_to_acres(22.4825, gsd_m=30.0) == pytest.approx(5.0, rel=1e-3)


def test_1000_acre_farm_case() -> None:
    """Test 1,000-acre farm boundary calculation at 30m GSD."""
    # 1000 acres ≈ 4,046,856.4 m²; 4,046,856.4 / 900 ≈ 4,496.5 pixels (≈ 67×67 grid)
    acres = 1000.0
    px = acres_to_pixels(acres, gsd_m=30.0)
    assert px == pytest.approx(4496.5, rel=1e-2)
    assert round(px ** 0.5) == 67
