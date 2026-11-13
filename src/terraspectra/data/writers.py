"""Multi-band hyperspectral and geospatial raster writers.

Supports:
- GeoTIFF writer with Rasterio (with graceful fallback to NPZ/memory-mapped raster when Rasterio is unavailable).
- Chunked HDF5 writer with h5py (with graceful fallback to NPZ/HDF5 simulation).
- CRS, affine transform, wavelength band descriptions, metadata tags, and nodata value handling.
- Tiled and compressed profiles.
- Label mask (uint8) and DEM (float32) raster writers.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

from terraspectra.core.constants import DEFAULT_CRS, GSD_M, NODATA


def write_geotiff(
    path: str | Path,
    cube: NDArray[np.float32],  # [B, H, W]
    wavelengths_nm: NDArray[np.float32] | list[float] | None = None,
    crs: str = DEFAULT_CRS,
    transform: tuple[float, float, float, float, float, float] | None = None,
    nodata: float = NODATA,
    compress: str = "deflate",
    tiled: bool = True,
    blockxsize: int = 256,
    blockysize: int = 256,
    metadata_tags: dict[str, str] | None = None,
) -> Path:
    """Write a 3D hyperspectral cube to GeoTIFF with CRS and band metadata.

    Args:
        path: Output destination path.
        cube: 3D float32 array in [B, H, W] format.
        wavelengths_nm: List or 1D array of center wavelengths in nm per band.
        crs: Coordinate reference system identifier string (default EPSG:32643).
        transform: 6-element GDAL/Affine transform tuple (c, a, b, f, d, e).
        nodata: Value representing nodata pixels (-9999.0).
        compress: Compression algorithm ('deflate', 'lzw', etc.).
        tiled: Whether to enable tiled/blocked TIFF layout.
        blockxsize: Tile width.
        blockysize: Tile height.
        metadata_tags: Optional dictionary of string key-value tags.

    Returns:
        Path to written file.
    """
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    b, h, w = cube.shape

    if transform is None:
        # Default origin at (500000.0, 3160000.0) in UTM 43N with 30m resolution
        # Affine: (west, pixel_width, 0, north, 0, -pixel_height)
        transform = (500000.0, float(GSD_M), 0.0, 3160000.0, 0.0, -float(GSD_M))

    try:
        import rasterio
        from rasterio.transform import Affine

        affine_obj = Affine(
            transform[1], transform[2], transform[0],
            transform[4], transform[5], transform[3]
        )

        profile = {
            "driver": "GTiff",
            "dtype": "float32",
            "count": b,
            "height": h,
            "width": w,
            "crs": crs,
            "transform": affine_obj,
            "nodata": nodata,
            "compress": compress,
            "tiled": tiled,
            "blockxsize": min(blockxsize, w),
            "blockysize": min(blockysize, h),
        }

        with rasterio.open(out_path, "w", **profile) as dst:
            dst.write(cube)
            if wavelengths_nm is not None:
                for idx, wl in enumerate(wavelengths_nm, start=1):
                    dst.set_band_description(idx, f"Wavelength {float(wl):.2f} nm")
            if metadata_tags:
                dst.update_tags(**metadata_tags)

    except ImportError:
        # Fallback format: structured NPZ container preserving full geo metadata
        npz_path = out_path.with_suffix(".npz")
        np.savez_compressed(
            npz_path,
            cube=cube,
            wavelengths_nm=np.asarray(wavelengths_nm) if wavelengths_nm is not None else np.array([]),
            crs=crs,
            transform=np.array(transform, dtype=np.float64),
            nodata=nodata,
            metadata=json.dumps(metadata_tags or {}),
        )
        # Create an accompanying JSON sidecar for standard raster parsers
        sidecar = out_path.with_suffix(".json")
        sidecar.write_text(
            json.dumps({
                "format": "GeoTIFF_fallback_npz",
                "bands": b, "rows": h, "cols": w,
                "crs": crs, "transform": list(transform),
                "nodata": nodata, "target": str(npz_path.name)
            }, indent=2),
            encoding="utf-8"
        )
        return npz_path

    return out_path


def write_hdf5(
    path: str | Path,
    cube: NDArray[np.float32],  # [B, H, W]
    wavelengths_nm: NDArray[np.float32] | list[float] | None = None,
    crs: str = DEFAULT_CRS,
    transform: tuple[float, float, float, float, float, float] | None = None,
    chunk_shape: tuple[int, int, int] = (32, 128, 128),
    compression: str = "gzip",
    compression_opts: int = 4,
    metadata_attrs: dict[str, Any] | None = None,
) -> Path:
    """Write a 3D hyperspectral cube to chunked HDF5 format with attributes.

    Args:
        path: Output destination path.
        cube: 3D float32 array [B, H, W].
        wavelengths_nm: Center wavelength array in nm.
        crs: CRS identifier string.
        transform: Affine geotransform tuple.
        chunk_shape: 3D chunking shape (e.g. 32 bands x 128 x 128).
        compression: Compression filter ('gzip' or 'lzf').
        compression_opts: Gzip compression level.
        metadata_attrs: Dictionary of custom dataset attributes.

    Returns:
        Path to written HDF5 file.
    """
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    b, h, w = cube.shape
    safe_chunks = (
        min(chunk_shape[0], b),
        min(chunk_shape[1], h),
        min(chunk_shape[2], w),
    )

    if transform is None:
        transform = (500000.0, float(GSD_M), 0.0, 3160000.0, 0.0, -float(GSD_M))

    try:
        import h5py

        with h5py.File(out_path, "w") as f:
            dset = f.create_dataset(
                "/cube",
                data=cube,
                chunks=safe_chunks,
                compression=compression,
                compression_opts=compression_opts if compression == "gzip" else None,
            )
            dset.attrs["crs"] = crs
            dset.attrs["transform"] = transform
            dset.attrs["gsd_m"] = GSD_M
            dset.attrs["nodata"] = NODATA

            if wavelengths_nm is not None:
                dset.attrs["wavelengths_nm"] = np.asarray(wavelengths_nm, dtype=np.float32)

            if metadata_attrs:
                for k, v in metadata_attrs.items():
                    dset.attrs[k] = str(v) if not isinstance(v, (int, float, str, bytes)) else v

    except ImportError:
        # Fallback container
        h5_npz = out_path.with_suffix(".npz")
        np.savez_compressed(
            h5_npz,
            cube=cube,
            wavelengths_nm=np.asarray(wavelengths_nm) if wavelengths_nm is not None else np.array([]),
            crs=crs,
            transform=np.array(transform, dtype=np.float64),
            chunks=np.array(safe_chunks),
            metadata=json.dumps(metadata_attrs or {}),
        )
        return h5_npz

    return out_path


def write_label_raster(
    path: str | Path,
    labels: NDArray[np.uint8],  # [H, W]
    crs: str = DEFAULT_CRS,
    transform: tuple[float, float, float, float, float, float] | None = None,
) -> Path:
    """Write integer classification label mask (0=healthy, 1=stress, 2=disease)."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    h, w = labels.shape
    c3d = labels.reshape(1, h, w).astype(np.float32)
    return write_geotiff(p, c3d, crs=crs, transform=transform, nodata=255.0)


def write_dem_raster(
    path: str | Path,
    dem_m: NDArray[np.float32],  # [H, W]
    crs: str = DEFAULT_CRS,
    transform: tuple[float, float, float, float, float, float] | None = None,
) -> Path:
    """Write digital elevation model (DEM) in metres."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    h, w = dem_m.shape
    c3d = dem_m.reshape(1, h, w)
    return write_geotiff(p, c3d, crs=crs, transform=transform, nodata=NODATA)
