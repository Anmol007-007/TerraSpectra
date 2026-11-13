"""Unit tests for raster writers, readers, windowing, and catalog indexing."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from terraspectra.data.catalog import SceneCatalog, scan_directory_for_scenes
from terraspectra.data.readers import get_reader
from terraspectra.data.windows import (
    Window,
    auto_chunk_size,
    estimate_cube_memory_mb,
    iter_blocks,
    iter_overlapping_windows,
)
from terraspectra.data.writers import write_geotiff, write_hdf5


def test_geotiff_and_reader_roundtrip(tmp_path: Path) -> None:
    """Test writing a 3D hyperspectral cube and reading windows back."""
    cube = np.random.rand(16, 64, 64).astype(np.float32)
    wls = np.linspace(400.0, 900.0, 16, dtype=np.float32)

    tif_path = tmp_path / "test_cube.tif"
    written_path = write_geotiff(tif_path, cube, wavelengths_nm=wls)

    reader = get_reader(written_path)
    assert reader.bands == 16
    assert reader.rows == 64
    assert reader.cols == 64

    # Test reading sub-window
    win = Window(row_off=10, col_off=10, height=20, width=20)
    sub = reader.read_window(win)
    assert sub.shape == (16, 20, 20)
    np.testing.assert_allclose(sub, cube[:, 10:30, 10:30], atol=1e-5)


def test_hdf5_and_reader_roundtrip(tmp_path: Path) -> None:
    """Test HDF5 chunked cube writing and reading."""
    cube = np.random.rand(8, 32, 32).astype(np.float32)
    wls = np.linspace(500.0, 800.0, 8, dtype=np.float32)

    h5_path = tmp_path / "test_cube.h5"
    written_path = write_hdf5(h5_path, cube, wavelengths_nm=wls)

    reader = get_reader(written_path)
    assert reader.bands == 8
    assert reader.rows == 32
    assert reader.cols == 32

    win = Window(row_off=0, col_off=0, height=16, width=16)
    sub = reader.read_window(win, bands=[0, 1, 2])
    assert sub.shape == (3, 16, 16)


def test_window_iterators() -> None:
    """Test block and overlapping window iterators cover spatial bounds."""
    rows, cols = 100, 100
    blocks = list(iter_blocks(rows, cols, block_h=30, block_w=30))
    # 4 rows x 4 cols = 16 blocks
    assert len(blocks) == 16

    # Verify coverage
    covered = np.zeros((rows, cols), dtype=int)
    for b in blocks:
        covered[b.row_off : b.row_off + b.height, b.col_off : b.col_off + b.width] += 1
    assert np.all(covered == 1)

    # Overlapping windows
    ov_windows = list(iter_overlapping_windows(rows, cols, tile_size=64, overlap=16))
    assert len(ov_windows) >= 4


def test_memory_and_auto_chunk() -> None:
    """Test RAM estimation and auto chunk size selection."""
    mb = estimate_cube_memory_mb(bands=224, rows=1024, cols=1024, dtype_bytes=4)
    assert 890.0 < mb < 900.0

    chunk = auto_chunk_size(bands=224, rows=1024, cols=1024, ram_budget_mb=100.0)
    assert chunk[0] < 1024
    assert chunk[0] >= 32


def test_scene_catalog(tmp_path: Path) -> None:
    """Test directory scanning and scene catalog persistence."""
    cube = np.random.rand(4, 16, 16).astype(np.float32)
    write_geotiff(tmp_path / "scene_a.tif", cube)
    write_hdf5(tmp_path / "scene_b.h5", cube)

    catalog = scan_directory_for_scenes(tmp_path)
    assert len(catalog.list_scenes()) == 2

    cat_json = tmp_path / "catalog.json"
    catalog.save(cat_json)
    loaded = SceneCatalog.load(cat_json)
    assert len(loaded.list_scenes()) == 2
