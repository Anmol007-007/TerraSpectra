"""Geospatial GDAL utilities, warping, reprojection, and clipping helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

from terraspectra.core.constants import DEFAULT_CRS, GSD_M


def gdalinfo_dict(file_path: str | Path) -> dict[str, Any]:
    """Inspect raster and return metadata dictionary similar to gdalinfo."""
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {p}")

    try:
        from osgeo import gdal
        ds = gdal.Open(str(p))
        if ds is not None:
            info = gdal.Info(ds, format="json")
            return json.loads(info) if isinstance(info, str) else info
    except (ImportError, Exception):
        pass

    # Fallback inspection
    from terraspectra.data.readers import get_reader
    try:
        reader = get_reader(p)
        return {
            "description": str(p),
            "driverShortName": "GTiff" if p.suffix in (".tif", ".tiff") else "HDF5",
            "size": [reader.cols, reader.rows],
            "bands": [
                {"band": i + 1, "wavelength_nm": float(reader.wavelengths_nm[i])}
                for i in range(reader.bands)
            ],
            "coordinateSystem": {"wkt": reader.crs},
            "geoTransform": list(reader.transform),
        }
    except Exception as e:
        return {"error": str(e), "path": str(p)}


def resample_gsd(
    cube: NDArray[np.float32],  # [B, H, W]
    current_gsd_m: float,
    target_gsd_m: float,
    order: int = 1,
) -> NDArray[np.float32]:
    """Resample raster array to target spatial ground sampling distance (GSD)."""
    if abs(current_gsd_m - target_gsd_m) < 1e-4:
        return cube

    zoom_factor = current_gsd_m / target_gsd_m
    from scipy.ndimage import zoom

    return zoom(cube, (1.0, zoom_factor, zoom_factor), order=order).astype(np.float32)


def clip_raster_to_bounds(
    cube: NDArray[np.float32],
    transform: tuple[float, float, float, float, float, float],
    west: float,
    south: float,
    east: float,
    north: float,
) -> tuple[NDArray[np.float32], tuple[float, float, float, float, float, float]]:
    """Clip 3D raster cube to spatial bounding box."""
    c_x, a_w, _, c_y, _, e_h = transform
    col_start = max(0, int(round((west - c_x) / a_w)))
    col_end = min(cube.shape[2], int(round((east - c_x) / a_w)))
    row_start = max(0, int(round((north - c_y) / e_h)))
    row_end = min(cube.shape[1], int(round((south - c_y) / e_h)))

    clipped = cube[:, row_start:row_end, col_start:col_end]
    new_origin_x = c_x + col_start * a_w
    new_origin_y = c_y + row_start * e_h
    new_transform = (new_origin_x, a_w, 0.0, new_origin_y, 0.0, e_h)
    return clipped, new_transform
