"""Unit tests for raster edge cases: empty rasters, nodata-only tiles, single-band rasters, and big-endian byteorder."""

from __future__ import annotations

from pathlib import Path
import numpy as np
import pytest

from terraspectra.core.constants import NODATA
from terraspectra.core.errors import EmptyRasterError
from terraspectra.data.readers import GeoTiffReader, Hdf5Reader, is_nodata_window
from terraspectra.data.windows import Window


def test_empty_raster_edge_case(tmp_path: Path) -> None:
    """Prove that empty rasters (0 bands, rows, or cols) raise EmptyRasterError."""
    # Create empty NPZ cube with 0 bands
    empty_file = tmp_path / "empty_scene.npz"
    np.savez(empty_file, cube=np.zeros((0, 10, 10), dtype=np.float32))

    with pytest.raises(EmptyRasterError):
        GeoTiffReader(empty_file)

    # 0 rows
    empty_rows = tmp_path / "empty_rows.npz"
    np.savez(empty_rows, cube=np.zeros((5, 0, 10), dtype=np.float32))
    with pytest.raises(EmptyRasterError):
        GeoTiffReader(empty_rows)


def test_nodata_only_tile_helper() -> None:
    """Validate is_nodata_window helper across NoData constants and NaNs."""
    # All NoData
    nodata_arr = np.full((10, 10), NODATA, dtype=np.float32)
    assert is_nodata_window(nodata_arr, nodata=NODATA) is True

    # Mixed with valid data
    mixed_arr = np.full((10, 10), NODATA, dtype=np.float32)
    mixed_arr[5, 5] = 0.42
    assert is_nodata_window(mixed_arr, nodata=NODATA) is False

    # NaNs
    nan_arr = np.full((5, 5), np.nan, dtype=np.float32)
    assert is_nodata_window(nan_arr) is True


def test_single_band_raster_handling(tmp_path: Path) -> None:
    """Verify single-band raster is promoted cleanly to 3D [1, H, W] tensor."""
    single_band_file = tmp_path / "single_band.npz"
    np.savez(single_band_file, cube=np.random.rand(1, 20, 20).astype(np.float32))

    reader = GeoTiffReader(single_band_file)
    assert reader.bands == 1
    assert reader.shape == (1, 20, 20)

    win = Window(row_off=0, col_off=0, height=10, width=10)
    data = reader.read_window(win)
    assert data.ndim == 3
    assert data.shape == (1, 10, 10)


def test_big_endian_dtype_handling(tmp_path: Path) -> None:
    """Ensure big-endian (>f4) arrays are automatically converted to native byteorder."""
    big_endian_arr = np.random.rand(4, 15, 15).astype(">f4")
    assert big_endian_arr.dtype.byteorder == ">"

    be_file = tmp_path / "big_endian_cube.npz"
    np.savez(be_file, cube=big_endian_arr)

    reader = GeoTiffReader(be_file)
    win = Window(row_off=0, col_off=0, height=8, width=8)
    res = reader.read_window(win)

    assert res.dtype == np.float32
    assert res.dtype.byteorder in ("=", "|")
    assert res.shape == (4, 8, 8)
