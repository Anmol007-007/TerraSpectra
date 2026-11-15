"""Spectral and spatial data augmentations for 3D hyperspectral tensors."""

from __future__ import annotations

from typing import Callable

import numpy as np
from numpy.typing import NDArray


class SpectralJitter:
    """Randomly scale or shift spectral band channels."""

    def __init__(self, scale_range: tuple[float, float] = (0.95, 1.05)) -> None:
        self.scale_range = scale_range

    def __call__(self, patch: NDArray[np.float32]) -> NDArray[np.float32]:
        # patch shape [C, D, H, W] or [D, H, W]
        scale = np.random.uniform(self.scale_range[0], self.scale_range[1])
        return (patch * scale).astype(np.float32)


class GaussianNoise:
    """Inject additive zero-mean Gaussian noise."""

    def __init__(self, sigma: float = 0.01) -> None:
        self.sigma = sigma

    def __call__(self, patch: NDArray[np.float32]) -> NDArray[np.float32]:
        noise = np.random.normal(0.0, self.sigma, size=patch.shape).astype(np.float32)
        return patch + noise


class BandDropout:
    """Randomly zero out a small subset of spectral channels."""

    def __init__(self, p: float = 0.05) -> None:
        self.p = p

    def __call__(self, patch: NDArray[np.float32]) -> NDArray[np.float32]:
        # Expects [1, D, H, W] or [D, H, W]
        out = patch.copy()
        d_axis = 1 if out.ndim == 4 else 0
        d_dim = out.shape[d_axis]

        mask = np.random.binomial(1, 1.0 - self.p, size=d_dim).astype(np.float32)
        if out.ndim == 4:
            out *= mask[None, :, None, None]
        else:
            out *= mask[:, None, None]
        return out


class RandomSpatialFlip:
    """Random horizontal and vertical flips and 90-degree rotations."""

    def __call__(self, patch: NDArray[np.float32]) -> NDArray[np.float32]:
        # Spatial axes are the last two (-2, -1)
        out = patch
        if np.random.rand() > 0.5:
            out = np.flip(out, axis=-1)  # horizontal flip
        if np.random.rand() > 0.5:
            out = np.flip(out, axis=-2)  # vertical flip
        k = np.random.choice([0, 1, 2, 3])
        if k > 0:
            out = np.rot90(out, k=k, axes=(-2, -1))
        return np.ascontiguousarray(out)


class Compose:
    """Sequential composition of augmentation transforms."""

    def __init__(self, transforms: list[Callable[[NDArray[np.float32]], NDArray[np.float32]]]) -> None:
        self.transforms = transforms

    def __call__(self, patch: NDArray[np.float32]) -> NDArray[np.float32]:
        for t in self.transforms:
            patch = t(patch)
        return patch
