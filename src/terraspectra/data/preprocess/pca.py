"""Incremental PCA dimensionality reduction for multi-gigabyte hyperspectral data."""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray
from sklearn.decomposition import IncrementalPCA

from terraspectra.core.constants import PCA_N_COMPONENTS
from terraspectra.data.readers import CubeReader
from terraspectra.data.windows import iter_blocks


class CubePCA:
    """Incremental Principal Component Analysis wrapper for memory-safe raster reduction."""

    def __init__(
        self,
        n_components: int = PCA_N_COMPONENTS,
        whiten: bool = False,
        batch_size: int = 5000,
    ) -> None:
        self.n_components = n_components
        self.whiten = whiten
        self.batch_size = batch_size
        self.model = IncrementalPCA(
            n_components=n_components,
            whiten=whiten,
            batch_size=batch_size,
        )
        self.is_fitted: bool = False

    def fit_from_reader(
        self,
        reader: CubeReader,
        block_size: int = 128,
        max_samples: int = 50000,
    ) -> CubePCA:
        """Fit IncrementalPCA across spatial windows from a CubeReader stream."""
        collected = 0
        for win in iter_blocks(reader.rows, reader.cols, block_h=block_size, block_w=block_size):
            block = reader.read_window(win)  # [B, H, W]
            b, h, w = block.shape
            flat = block.reshape(b, -1).T  # [N_pixels, B]

            if flat.shape[0] >= self.n_components:
                self.model.partial_fit(flat)
                collected += flat.shape[0]

            if collected >= max_samples:
                break

        self.is_fitted = True
        return self

    def fit_array(self, X: NDArray[np.float32]) -> CubePCA:
        """Fit directly on 2D array [N_samples, n_features] or 3D cube [B, H, W]."""
        if X.ndim == 3:
            b, h, w = X.shape
            flat = X.reshape(b, -1).T
        else:
            flat = X
        self.model.fit(flat)
        self.is_fitted = True
        return self

    def transform_cube(self, cube: NDArray[np.float32]) -> NDArray[np.float32]:
        """Project 3D cube [B, H, W] into PCA space [n_components, H, W]."""
        if not self.is_fitted:
            raise RuntimeError("CubePCA model must be fitted before calling transform.")

        b, h, w = cube.shape
        flat = cube.reshape(b, -1).T  # [N_pixels, B]
        reduced = self.model.transform(flat)  # [N_pixels, n_components]
        return reduced.T.reshape(self.n_components, h, w).astype(np.float32)

    def inverse_transform_cube(self, pca_cube: NDArray[np.float32]) -> NDArray[np.float32]:
        """Reconstruct original spectral channels from PCA components."""
        k, h, w = pca_cube.shape
        flat = pca_cube.reshape(k, -1).T
        recon = self.model.inverse_transform(flat)
        b = recon.shape[1]
        return recon.T.reshape(b, h, w).astype(np.float32)

    def reconstruction_error(self, cube: NDArray[np.float32]) -> float:
        """Calculate Root Mean Squared Error (RMSE) of PCA reconstruction."""
        pca_proj = self.transform_cube(cube)
        recon = self.inverse_transform_cube(pca_proj)
        return float(np.sqrt(np.mean((cube - recon) ** 2)))

    def explained_variance_summary(self) -> dict[str, Any]:
        """Summary metrics of variance explained by the components."""
        if not self.is_fitted:
            return {"fitted": False}
        evr = self.model.explained_variance_ratio_
        return {
            "n_components": self.n_components,
            "total_explained_variance_ratio": float(np.sum(evr)),
            "per_component_variance_ratio": [float(x) for x in evr],
        }

    def save(self, path: str | Path) -> None:
        """Persist fitted PCA model to disk via pickle/joblib."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, path: str | Path) -> CubePCA:
        """Load fitted PCA model from disk."""
        with open(path, "rb") as f:
            return pickle.load(f)

