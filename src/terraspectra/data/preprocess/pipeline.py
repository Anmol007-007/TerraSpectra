"""End-to-end preprocessing pipeline composing cleaning, normalization, and PCA."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

from terraspectra.core.constants import PCA_N_COMPONENTS
from terraspectra.core.paths import ensure_dir
from terraspectra.data.preprocess.clean import (
    clean_nan_and_inf,
    clip_reflectance,
    drop_bad_bands,
    generate_qa_report,
    remove_spectral_spikes,
    smooth_savgol,
)
from terraspectra.data.preprocess.normalize import (
    BandStats,
    WelfordAccumulator,
    standardize_cube,
)
from terraspectra.data.preprocess.pca import CubePCA
from terraspectra.data.readers import CubeReader, get_reader


@dataclass
class PreprocessedScene:
    """Output container of the end-to-end preprocessing pipeline."""

    scene_id: str
    cleaned_cube: NDArray[np.float32]  # [B_clean, H, W]
    pca_cube: NDArray[np.float32]  # [PCA_components, H, W]
    valid_wavelengths_nm: NDArray[np.float32]
    valid_band_mask: NDArray[np.bool_]
    qa_report: dict[str, Any]


class PreprocessingPipeline:
    """Configurable pipeline: clean -> standardize -> PCA reduction."""

    def __init__(
        self,
        pca_components: int = PCA_N_COMPONENTS,
        smooth: bool = True,
        remove_spikes: bool = True,
    ) -> None:
        self.pca_components = pca_components
        self.smooth = smooth
        self.remove_spikes = remove_spikes
        self.band_stats: BandStats | None = None
        self.pca_model: CubePCA | None = None

    def fit_from_reader(self, reader: CubeReader) -> PreprocessingPipeline:
        """Fit normalization stats and IncrementalPCA on reference reader."""
        raw = reader.read_full()
        wls = reader.wavelengths_nm

        # Clean
        cleaned, valid_wls, _ = drop_bad_bands(raw, wls)
        cleaned, _ = clean_nan_and_inf(cleaned)
        if self.remove_spikes:
            cleaned = remove_spectral_spikes(cleaned)
        if self.smooth:
            cleaned = smooth_savgol(cleaned)
        cleaned = clip_reflectance(cleaned)

        # Fit Welford stats
        acc = WelfordAccumulator(n_bands=cleaned.shape[0])
        acc.update(cleaned)
        self.band_stats = acc.finalize()

        # Standardize for PCA
        std_cube = standardize_cube(cleaned, self.band_stats)

        # Fit PCA
        self.pca_model = CubePCA(n_components=self.pca_components)
        self.pca_model.fit_array(std_cube)

        return self

    def process_cube(
        self,
        cube: NDArray[np.float32],
        wavelengths_nm: NDArray[np.float32],
        scene_id: str = "scene",
    ) -> PreprocessedScene:
        """Execute full cleaning, normalization, and PCA transformation on a cube."""
        # 1. Clean
        cleaned, valid_wls, valid_mask = drop_bad_bands(cube, wavelengths_nm)
        cleaned, _ = clean_nan_and_inf(cleaned)
        if self.remove_spikes:
            cleaned = remove_spectral_spikes(cleaned)
        if self.smooth:
            cleaned = smooth_savgol(cleaned)
        cleaned = clip_reflectance(cleaned)

        # QA report
        qa = generate_qa_report(cube, cleaned, valid_mask)

        # 2. Standardize
        if self.band_stats is not None:
            std_cube = standardize_cube(cleaned, self.band_stats)
        else:
            acc = WelfordAccumulator(n_bands=cleaned.shape[0])
            acc.update(cleaned)
            self.band_stats = acc.finalize()
            std_cube = standardize_cube(cleaned, self.band_stats)

        # 3. PCA transform
        if self.pca_model is None or not self.pca_model.is_fitted:
            self.pca_model = CubePCA(n_components=min(self.pca_components, cleaned.shape[0]))
            self.pca_model.fit_array(std_cube)

        pca_cube = self.pca_model.transform_cube(std_cube)

        return PreprocessedScene(
            scene_id=scene_id,
            cleaned_cube=cleaned,
            pca_cube=pca_cube,
            valid_wavelengths_nm=valid_wls,
            valid_band_mask=valid_mask,
            qa_report=qa,
        )

    def process_and_cache(
        self,
        scene_path: str | Path,
        output_dir: str | Path,
    ) -> Path:
        """Process a scene from disk and cache the resulting PCA cube as .npy."""
        reader = get_reader(scene_path)
        scene = self.process_cube(reader.read_full(), reader.wavelengths_nm, scene_id=reader.path.stem)

        out_d = ensure_dir(output_dir)
        npy_path = out_d / f"{scene.scene_id}_pca{self.pca_components}.npy"
        np.save(npy_path, scene.pca_cube)
        return npy_path

