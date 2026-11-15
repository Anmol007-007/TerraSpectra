"""PyTorch Dataset for memory-efficient 3D hyperspectral patch sampling."""

from __future__ import annotations

from typing import Any, Callable

import numpy as np
try:
    import torch
    from torch.utils.data import Dataset
except ImportError:
    # Lightweight mock/fallback when torch is not installed in the active environment
    class Dataset:  # type: ignore[no-redef]
        def __len__(self) -> int:
            raise NotImplementedError
        def __getitem__(self, idx: int) -> Any:
            raise NotImplementedError

    class _TorchMock:
        long = "long"
        float32 = "float32"
        @staticmethod
        def from_numpy(arr: np.ndarray) -> np.ndarray:
            return arr
        @staticmethod
        def tensor(val: Any, dtype: Any = None) -> np.ndarray:
            return np.array(val)
        @staticmethod
        def stack(tensors: list[Any]) -> np.ndarray:
            return np.stack(tensors)
        @staticmethod
        def initial_seed() -> int:
            return 42

    torch = _TorchMock()  # type: ignore[assignment]

from terraspectra.data.patches import PatchSpec, extract_patch_with_padding
from terraspectra.data.readers import CubeReader


class HyperspectralPatchDataset(Dataset):
    """Memory-safe PyTorch Dataset serving 3D tensor patches [1, D, H, W].

    Integrates lazy windowed extraction from reference cubes.
    """

    def __init__(
        self,
        cube_or_reader: CubeReader | np.ndarray,
        patch_specs: list[PatchSpec],
        transform: Callable[[np.ndarray], np.ndarray] | None = None,
    ) -> None:
        self.cube_or_reader = cube_or_reader
        self.patch_specs = patch_specs
        self.transform = transform

        if isinstance(cube_or_reader, np.ndarray):
            self._cached_cube: np.ndarray | None = cube_or_reader
        else:
            self._cached_cube = None

    def __len__(self) -> int:
        return len(self.patch_specs)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        spec = self.patch_specs[idx]

        # Extract patch [D, H, W]
        if self._cached_cube is not None:
            raw_patch = extract_patch_with_padding(
                self._cached_cube,
                center_r=spec.center_r,
                center_c=spec.center_c,
                patch_size=spec.patch_size,
            )
        else:
            # Window read around center pixel
            from terraspectra.data.windows import Window

            half = spec.half_size
            r0 = max(0, spec.center_r - half)
            c0 = max(0, spec.center_c - half)
            win = Window(row_off=r0, col_off=c0, height=spec.patch_size, width=spec.patch_size)
            raw_patch = self.cube_or_reader.read_window(win)  # type: ignore[union-attr]

        if self.transform is not None:
            raw_patch = self.transform(raw_patch)

        # Reshape to 4D tensor with channel=1: [1, D, H, W] for 3D CNN stem
        patch_4d = raw_patch[None, ...].astype(np.float32)

        return {
            "patch": torch.from_numpy(patch_4d),
            "state": torch.tensor(spec.state_label, dtype=torch.long),
            "severity": torch.tensor(spec.severity, dtype=torch.float32),
            "days_to_symptoms": torch.tensor(spec.days_to_symptoms, dtype=torch.float32),
            "center": torch.tensor([spec.center_r, spec.center_c], dtype=torch.long),
            "scene_id": spec.scene_id,
        }


def custom_collate_fn(batch: list[dict[str, Any]]) -> dict[str, Any]:
    """Custom batch collate function aggregating 4D patch tensors and targets."""
    patches = torch.stack([item["patch"] for item in batch])
    states = torch.stack([item["state"] for item in batch])
    severities = torch.stack([item["severity"] for item in batch])
    days = torch.stack([item["days_to_symptoms"] for item in batch])
    centers = torch.stack([item["center"] for item in batch])
    scene_ids = [item["scene_id"] for item in batch]

    return {
        "patches": patches,  # [B_batch, 1, D, H, W]
        "states": states,  # [B_batch]
        "severities": severities,  # [B_batch]
        "days_to_symptoms": days,  # [B_batch]
        "centers": centers,  # [B_batch, 2]
        "scene_ids": scene_ids,
    }


def seed_worker(worker_id: int) -> None:
    """Worker initialization function for PyTorch DataLoader determinism."""
    worker_seed = torch.initial_seed() % (2**32)
    np.random.seed(worker_seed)
