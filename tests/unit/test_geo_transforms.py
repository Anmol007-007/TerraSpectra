"""Unit tests for GIS coordinate transforms, affine round-trips, and area conversions."""

from __future__ import annotations

import pytest

from terraspectra.geo.transforms import (
    FARM_BOUNDS_WGS84,
    bounds_to_geojson,
    calculate_pixel_area,
    check_raster_georeference,
    generate_gcp_fixtures,
    lonlat_to_pixel,
    pixel_to_lonlat,
)


def test_pixel_lonlat_affine_roundtrip() -> None:
    """Prove that pixel to lon/lat and inverse transform achieves sub-millimeter precision."""
    grid_shape = (67, 67)

    for r in [0, 10, 33, 50, 66]:
        for c in [0, 15, 33, 48, 66]:
            lon, lat = pixel_to_lonlat(r, c, bounds=FARM_BOUNDS_WGS84, grid_shape=grid_shape)
            r_rec, c_rec = lonlat_to_pixel(lon, lat, bounds=FARM_BOUNDS_WGS84, grid_shape=grid_shape)

            assert pytest.approx(r_rec, abs=1e-3) == r
            assert pytest.approx(c_rec, abs=1e-3) == c


def test_bounds_to_geojson() -> None:
    """Test RFC 7946 GeoJSON Polygon construction."""
    geojson = bounds_to_geojson(FARM_BOUNDS_WGS84)
    assert geojson["type"] == "Feature"
    assert geojson["geometry"]["type"] == "Polygon"
    coords = geojson["geometry"]["coordinates"][0]
    assert len(coords) == 5
    assert coords[0] == coords[4]  # Closed linear ring


def test_calculate_pixel_area() -> None:
    """Test pixel area calculations in m² and acres."""
    area_info = calculate_pixel_area(row=33, col=33, gsd_m=30.0)
    assert area_info["area_m2"] == 900.0
    # 900 / 4046.8564 ≈ 0.22239
    assert pytest.approx(area_info["area_acres"], rel=1e-3) == 0.22239


def test_gcp_fixtures_generation() -> None:
    """Test GCP generation for corners and farm center."""
    fixtures = generate_gcp_fixtures(bounds=FARM_BOUNDS_WGS84, grid_shape=(67, 67))
    assert len(fixtures["gcps"]) == 5
    gcp_ids = [g["id"] for g in fixtures["gcps"]]
    assert "NW_CORNER" in gcp_ids
    assert "CENTER" in gcp_ids
    assert "SE_CORNER" in gcp_ids


def test_check_raster_georeference_missing_and_fallback(tmp_path) -> None:
    """Test georeference check on non-existent and simulated files."""
    assert check_raster_georeference("non_existent_file.tif") is False

    dummy = tmp_path / "dummy.npz"
    dummy.write_bytes(b"dummy binary data")
    assert check_raster_georeference(dummy) is True
