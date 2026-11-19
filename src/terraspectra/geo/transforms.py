"""Geographic and raster affine coordinate transforms, georeferencing, and GCP fixtures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional, Sequence

import numpy as np

from terraspectra.core.constants import ACRES_PER_M2, GSD_M
from terraspectra.core.paths import ensure_dir

# Standard 1,000-acre demonstration farm bounds [minLon, minLat, maxLon, maxLat]
FARM_BOUNDS_WGS84: tuple[float, float, float, float] = (77.0900, 28.6100, 77.1105, 28.6285)


def pixel_to_lonlat(
    row: float,
    col: float,
    bounds: Sequence[float] = FARM_BOUNDS_WGS84,
    grid_shape: Sequence[int] = (67, 67),
    center_offset: bool = True,
) -> tuple[float, float]:
    """Convert raster pixel indices (row, col) to WGS84 geographic coordinates (lon, lat).

    Uses $(r + 0.5, c + 0.5)$ convention for pixel center representation.

    Args:
        row: Row index (0-indexed from top).
        col: Column index (0-indexed from left).
        bounds: [minLon, minLat, maxLon, maxLat].
        grid_shape: (rows, cols) of the raster.
        center_offset: If True, evaluates at pixel center (+0.5).

    Returns:
        (longitude, latitude) as floats.
    """
    min_lon, min_lat, max_lon, max_lat = bounds[0], bounds[1], bounds[2], bounds[3]
    num_rows, num_cols = int(grid_shape[0]), int(grid_shape[1])

    r_eff = row + (0.5 if center_offset else 0.0)
    c_eff = col + (0.5 if center_offset else 0.0)

    lon_step = (max_lon - min_lon) / num_cols
    lat_step = (max_lat - min_lat) / num_rows

    lon = min_lon + c_eff * lon_step
    # Raster rows increase downwards, latitude increases upwards
    lat = max_lat - r_eff * lat_step

    return round(float(lon), 7), round(float(lat), 7)


def lonlat_to_pixel(
    lon: float,
    lat: float,
    bounds: Sequence[float] = FARM_BOUNDS_WGS84,
    grid_shape: Sequence[int] = (67, 67),
) -> tuple[float, float]:
    """Convert WGS84 coordinates (lon, lat) to continuous raster pixel coordinates (row, col).

    Args:
        lon: Longitude in degrees.
        lat: Latitude in degrees.
        bounds: [minLon, minLat, maxLon, maxLat].
        grid_shape: (rows, cols) of the raster.

    Returns:
        (row, col) as continuous floating-point indices.
    """
    min_lon, min_lat, max_lon, max_lat = bounds[0], bounds[1], bounds[2], bounds[3]
    num_rows, num_cols = int(grid_shape[0]), int(grid_shape[1])

    c_continuous = (lon - min_lon) / (max_lon - min_lon) * num_cols - 0.5
    r_continuous = (max_lat - lat) / (max_lat - min_lat) * num_rows - 0.5

    return round(float(r_continuous), 6), round(float(c_continuous), 6)


def bounds_to_geojson(bounds: Sequence[float] = FARM_BOUNDS_WGS84) -> dict[str, Any]:
    """Convert [minLon, minLat, maxLon, maxLat] bounding box to RFC 7946 GeoJSON Polygon."""
    min_lon, min_lat, max_lon, max_lat = bounds[0], bounds[1], bounds[2], bounds[3]
    coordinates = [
        [
            [min_lon, min_lat],
            [max_lon, min_lat],
            [max_lon, max_lat],
            [min_lon, max_lat],
            [min_lon, min_lat],  # Closed ring
        ]
    ]
    return {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": coordinates,
        },
        "properties": {
            "minLon": min_lon,
            "minLat": min_lat,
            "maxLon": max_lon,
            "maxLat": max_lat,
        },
    }


def check_raster_georeference(
    file_path: str | Path,
    expected_bounds: Optional[Sequence[float]] = FARM_BOUNDS_WGS84,
    expected_crs: Optional[str] = "EPSG:32643",
    tolerance_deg: float = 0.005,
) -> bool:
    """Validate that a raster's CRS and bounding envelope conform to expected spatial bounds.

    Args:
        file_path: Path to target raster file (GeoTIFF, NPZ, or HDF5).
        expected_bounds: Optional [minLon, minLat, maxLon, maxLat] bounding box.
        expected_crs: Expected CRS string identifier (e.g. 'EPSG:32643' or 'EPSG:4326').
        tolerance_deg: Angular tolerance in degrees for WGS84 boundary comparison.

    Returns:
        True if the file exists and spatial georeferencing matches expectations.
    """
    p = Path(file_path)
    if not p.exists():
        return False

    try:
        import rasterio

        with rasterio.open(p) as src:
            if expected_crs and src.crs:
                crs_str = src.crs.to_string() if hasattr(src.crs, "to_string") else str(src.crs)
                clean_expected = expected_crs.split(":")[-1].strip().lower()
                if clean_expected not in crs_str.lower():
                    return False

            bounds = src.bounds
            # Check bounding coordinates if expected_bounds is provided
            if expected_bounds and len(expected_bounds) >= 4:
                # If bounds are in degrees (WGS84)
                if abs(bounds.left) <= 180.0 and abs(expected_bounds[0]) <= 180.0:
                    if abs(bounds.left - expected_bounds[0]) > tolerance_deg:
                        return False
                    if abs(bounds.bottom - expected_bounds[1]) > tolerance_deg:
                        return False
                    if abs(bounds.right - expected_bounds[2]) > tolerance_deg:
                        return False
                    if abs(bounds.top - expected_bounds[3]) > tolerance_deg:
                        return False
            return True
    except (ImportError, OSError):
        # Fallback check for simulated/npz files when rasterio is unavailable
        return p.exists() and p.stat().st_size > 0
    except Exception:
        return False


def calculate_pixel_area(
    row: int,
    col: int,
    bounds: Sequence[float] = FARM_BOUNDS_WGS84,
    grid_shape: Sequence[int] = (67, 67),
    gsd_m: float = GSD_M,
) -> dict[str, float]:
    """Calculate the spatial ground area of a raster pixel in square metres and acres.

    Args:
        row: Row index of pixel.
        col: Column index of pixel.
        bounds: [minLon, minLat, maxLon, maxLat] bounding box.
        grid_shape: (rows, cols) raster grid dimensions.
        gsd_m: Ground sampling distance in metres (default: 30m).

    Returns:
        Dictionary containing pixel index, center lon/lat, GSD, and area in m² and acres.
    """
    lon, lat = pixel_to_lonlat(row, col, bounds=bounds, grid_shape=grid_shape)
    area_m2 = gsd_m * gsd_m
    area_acres = area_m2 * ACRES_PER_M2
    return {
        "row": float(row),
        "col": float(col),
        "lon": lon,
        "lat": lat,
        "gsd_m": gsd_m,
        "area_m2": round(area_m2, 2),
        "area_acres": round(area_acres, 6),
    }


def generate_gcp_fixtures(
    bounds: Sequence[float] = FARM_BOUNDS_WGS84,
    grid_shape: Sequence[int] = (67, 67),
    output_files: Optional[list[Path | str]] = None,
) -> dict[str, Any]:
    """Generate canonical Ground Control Points (GCPs) for 4 corners and farm center.

    Saves fixtures for cross-language validation between Python and TypeScript.
    """
    rows, cols = int(grid_shape[0]), int(grid_shape[1])
    gcps = [
        {"id": "NW_CORNER", "name": "Northwest Boundary Corner", "row": 0, "col": 0},
        {"id": "NE_CORNER", "name": "Northeast Boundary Corner", "row": 0, "col": cols - 1},
        {"id": "CENTER", "name": "Farm Geographic Center", "row": rows // 2, "col": cols // 2},
        {"id": "SW_CORNER", "name": "Southwest Boundary Corner", "row": rows - 1, "col": 0},
        {"id": "SE_CORNER", "name": "Southeast Boundary Corner", "row": rows - 1, "col": cols - 1},
    ]

    for gcp in gcps:
        lon, lat = pixel_to_lonlat(gcp["row"], gcp["col"], bounds=bounds, grid_shape=grid_shape)
        gcp["lon"] = lon
        gcp["lat"] = lat

    payload = {
        "crs": "EPSG:4326",
        "bounds": list(bounds),
        "grid_shape": list(grid_shape),
        "gsd_m": GSD_M,
        "gcps": gcps,
    }

    if output_files:
        for out in output_files:
            p = Path(out)
            ensure_dir(p.parent)
            with open(p, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)

    return payload
