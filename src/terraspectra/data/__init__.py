"""Data pipeline package exports."""

from terraspectra.data.catalog import SceneCatalog, scan_directory_for_scenes
from terraspectra.data.readers import (
    CubeReader,
    GeoTiffReader,
    Hdf5Reader,
    get_reader,
)
from terraspectra.data.windows import (
    Window,
    WindowLRUCache,
    auto_chunk_size,
    estimate_cube_memory_mb,
    iter_blocks,
    iter_overlapping_windows,
)
from terraspectra.data.writers import (
    write_dem_raster,
    write_geotiff,
    write_hdf5,
    write_label_raster,
)

__all__ = [
    "write_geotiff",
    "write_hdf5",
    "write_label_raster",
    "write_dem_raster",
    "CubeReader",
    "GeoTiffReader",
    "Hdf5Reader",
    "get_reader",
    "Window",
    "WindowLRUCache",
    "iter_blocks",
    "iter_overlapping_windows",
    "estimate_cube_memory_mb",
    "auto_chunk_size",
    "SceneCatalog",
    "scan_directory_for_scenes",
]
