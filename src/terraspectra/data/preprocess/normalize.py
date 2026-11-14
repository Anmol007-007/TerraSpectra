"""Streaming per-band normalisation, Welford statistics, continuum removal, and SNV."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray


@dataclass
class BandStats:
    """Per-band streaming summary statistics (Welford algorithm)."""

    count: int
    mean: NDArray[np.float32]  # [B]
    std: NDArray[np.float32]  # [B]
    min_val: NDArray[np.float32]  # [B]
    max_val: NDArray[np.float32]  # [B]

    def save(self, path: str | Path) -> None:
        """Save statistics to compressed NPZ archive."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            p,
            count=self.count,
            mean=self.mean,
            std=self.std,
            min_val=self.min_val,
            max_val=self.max_val,
        )

    @classmethod
    def load(cls, path: str | Path) -> BandStats:
        """Load statistics from NPZ archive."""
        data = np.load(path)
        return cls(
            count=int(data["count"]),
            mean=data["mean"],
            std=data["std"],
            min_val=data["min_val"],
            max_val=data["max_val"],
        )


class WelfordAccumulator:
    """Numerically stable streaming calculation of mean and variance across scenes/windows."""

    def __init__(self, n_bands: int) -> None:
        self.n_bands = n_bands
        self.count: int = 0
        self.mean = np.zeros(n_bands, dtype=np.float64)
        self.M2 = np.zeros(n_bands, dtype=np.float64)
        self.min_val = np.full(n_bands, np.inf, dtype=np.float32)
        self.max_val = np.full(n_bands, -np.inf, dtype=np.float32)

    def update(self, block: NDArray[np.float32]) -> None:
        """Update running statistics with a 3D block [B, H, W]."""
        b, h, w = block.shape
        flat = block.reshape(b, -1)  # [B, N_px]
        n_px = flat.shape[1]
        if n_px == 0:
            return

        batch_mean = np.mean(flat, axis=1)
        batch_var = np.var(flat, axis=1)
        batch_M2 = batch_var * n_px

        if self.count == 0:
            self.count = n_px
            self.mean = batch_mean
            self.M2 = batch_M2
            self.min_val = np.min(flat, axis=1).astype(np.float32)
            self.max_val = np.max(flat, axis=1).astype(np.float32)
        else:
            new_count = self.count + n_px
            delta = batch_mean - self.mean
            self.mean += delta * (n_px / new_count)
            self.M2 += batch_M2 + (delta ** 2) * (self.count * n_px / new_count)
            self.count = new_count
            self.min_val = np.minimum(self.min_val, np.min(flat, axis=1))
            self.max_val = np.maximum(self.max_val, np.max(flat, axis=1))

    def finalize(self) -> BandStats:
        """Compute final standard deviation and return BandStats container."""
        variance = self.M2 / max(1, self.count - 1)
        std = np.sqrt(np.maximum(1e-8, variance)).astype(np.float32)
        return BandStats(
            count=self.count,
            mean=self.mean.astype(np.float32),
            std=std,
            min_val=self.min_val,
            max_val=self.max_val,
        )


def standardize_cube(
    cube: NDArray[np.float32],
    stats: BandStats,
    eps: float = 1e-6,
) -> NDArray[np.float32]:
    """Z-score standardisation: (X - mean) / (std + eps) along spectral axis."""
    mean_3d = stats.mean[:, None, None]
    std_3d = (stats.std + eps)[:, None, None]
    return ((cube - mean_3d) / std_3d).astype(np.float32)


def min_max_normalize_cube(
    cube: NDArray[np.float32],
    stats: BandStats,
    eps: float = 1e-6,
) -> NDArray[np.float32]:
    """Min-max scaling to [0, 1] per band using recorded statistics."""
    min_3d = stats.min_val[:, None, None]
    max_3d = stats.max_val[:, None, None]
    diff = np.maximum(eps, max_3d - min_3d)
    return np.clip((cube - min_3d) / diff, 0.0, 1.0).astype(np.float32)


def standard_normal_variate(cube: NDArray[np.float32]) -> NDArray[np.float32]:
    """Standard Normal Variate (SNV) pixel-wise spectral normalisation."""
    b, h, w = cube.shape
    px_mean = np.mean(cube, axis=0, keepdims=True)
    px_std = np.std(cube, axis=0, keepdims=True) + 1e-6
    return ((cube - px_mean) / px_std).astype(np.float32)


def continuum_removal(
    cube: NDArray[np.float32],
    wavelengths_nm: NDArray[np.float32],
) -> NDArray[np.float32]:
    """Continuum removal by normalizing to convex hull envelope per pixel."""
    from scipy.spatial import ConvexHull

    b, h, w = cube.shape
    flat = cube.reshape(b, -1)  # [B, N]
    cr_flat = np.ones_like(flat, dtype=np.float32)

    # Simplified fast linear continuum between endpoints
    # Baseline line between first and last valid band
    w0, w1 = wavelengths_nm[0], wavelengths_nm[-1]
    slope = (flat[-1, :] - flat[0, :]) / (w1 - w0 + 1e-6)
    for i, wl in enumerate(wavelengths_nm):
        hull_val = flat[0, :] + slope * (wl - w0)
        cr_flat[i, :] = np.clip(flat[i, :] / np.maximum(1e-4, hull_val), 0.0, 1.5)

    return cr_flat.reshape(b, h, w)

