"""Spatial and temporal data partitioning without spatial leakage."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

from terraspectra.data.patches import PatchSpec


@dataclass
class SplitManifest:
    """Persistent record of train, val, test partition indices."""

    train_indices: list[int]
    val_indices: list[int]
    test_indices: list[int]
    method: str
    buffer_pixels: int
    seed: int

    def save(self, path: str | Path) -> Path:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")
        return p

    @classmethod
    def load(cls, path: str | Path) -> SplitManifest:
        p = Path(path)
        data = json.loads(p.read_text(encoding="utf-8"))
        return cls(**data)


def spatial_block_split(
    patch_specs: list[PatchSpec],
    grid_rows: int = 128,
    grid_cols: int = 128,
    block_size: int = 32,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    buffer_pixels: int = 2,
    seed: int = 42,
) -> tuple[list[int], list[int], list[int]]:
    """Split patches into train, val, and test using non-overlapping spatial blocks.

    Enforces a spatial buffer zone of `buffer_pixels` around block boundaries to prevent
    information leakage across splits.
    """
    rng = np.random.default_rng(seed)

    n_blocks_r = (grid_rows + block_size - 1) // block_size
    n_blocks_c = (grid_cols + block_size - 1) // block_size
    total_blocks = n_blocks_r * n_blocks_c

    block_ids = np.arange(total_blocks)
    rng.shuffle(block_ids)

    n_train_blocks = int(round(total_blocks * train_ratio))
    n_val_blocks = int(round(total_blocks * val_ratio))

    train_blocks = set(block_ids[:n_train_blocks])
    val_blocks = set(block_ids[n_train_blocks : n_train_blocks + n_val_blocks])
    test_blocks = set(block_ids[n_train_blocks + n_val_blocks :])

    train_idx: list[int] = []
    val_idx: list[int] = []
    test_idx: list[int] = []

    for i, spec in enumerate(patch_specs):
        r, c = spec.center_r, spec.center_c

        # Check block coordinates
        b_r = r // block_size
        b_c = c // block_size
        b_id = b_r * n_blocks_c + b_c

        # Boundary buffer check: discard samples within buffer_pixels of block edge
        r_rem = r % block_size
        c_rem = c % block_size
        is_near_edge = (
            r_rem < buffer_pixels
            or r_rem >= (block_size - buffer_pixels)
            or c_rem < buffer_pixels
            or c_rem >= (block_size - buffer_pixels)
        )
        if is_near_edge:
            continue

        if b_id in train_blocks:
            train_idx.append(i)
        elif b_id in val_blocks:
            val_idx.append(i)
        elif b_id in test_blocks:
            test_idx.append(i)

    return train_idx, val_idx, test_idx
