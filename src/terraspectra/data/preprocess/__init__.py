"""Preprocessing subpackage exports."""

from terraspectra.data.preprocess.clean import (
    clean_nan_and_inf,
    clip_reflectance,
    drop_bad_bands,
    generate_qa_report,
    remove_spectral_spikes,
    smooth_savgol,
)
from terraspectra.data.preprocess.indices import (
    build_index_stack,
    compute_cire,
    compute_mcari,
    compute_ndvi,
    compute_ndwi,
    compute_pri,
    compute_red_edge_position,
)
from terraspectra.data.preprocess.normalize import (
    BandStats,
    WelfordAccumulator,
    continuum_removal,
    min_max_normalize_cube,
    standard_normal_variate,
    standardize_cube,
)
from terraspectra.data.preprocess.pca import CubePCA
from terraspectra.data.preprocess.pipeline import (
    PreprocessedScene,
    PreprocessingPipeline,
)

__all__ = [
    "drop_bad_bands",
    "clean_nan_and_inf",
    "remove_spectral_spikes",
    "smooth_savgol",
    "clip_reflectance",
    "generate_qa_report",
    "BandStats",
    "WelfordAccumulator",
    "standardize_cube",
    "min_max_normalize_cube",
    "standard_normal_variate",
    "continuum_removal",
    "compute_ndvi",
    "compute_pri",
    "compute_ndwi",
    "compute_cire",
    "compute_red_edge_position",
    "compute_mcari",
    "build_index_stack",
    "CubePCA",
    "PreprocessedScene",
    "PreprocessingPipeline",
]
