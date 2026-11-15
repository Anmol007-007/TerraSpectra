"""Data package exports."""

from terraspectra.data.augment import (
    BandDropout,
    Compose,
    GaussianNoise,
    RandomSpatialFlip,
    SpectralJitter,
)
from terraspectra.data.catalog import SceneCatalog, scan_directory_for_scenes
from terraspectra.data.dataset import (
    HyperspectralPatchDataset,
    custom_collate_fn,
    seed_worker,
)
from terraspectra.data.loaders import build_dataloader
from terraspectra.data.patches import (
    PatchSpec,
    build_patch_index,
    extract_patch_with_padding,
    save_patch_index_npz,
)
from terraspectra.data.readers import (
    CubeReader,
    GeoTiffReader,
    Hdf5Reader,
    get_reader,
)
from terraspectra.data.splits import (
    SplitManifest,
    spatial_block_split,
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
    "PatchSpec",
    "extract_patch_with_padding",
    "build_patch_index",
    "save_patch_index_npz",
    "HyperspectralPatchDataset",
    "custom_collate_fn",
    "seed_worker",
    "build_dataloader",
    "SplitManifest",
    "spatial_block_split",
    "SpectralJitter",
    "GaussianNoise",
    "BandDropout",
    "RandomSpatialFlip",
    "Compose",
]
