"""Spatial patch extraction with reflection border padding and index generation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True)
class PatchSpec:
    """Specification of a spatial patch centered at (center_r, center_c)."""

    center_r: int
    center_c: int
    patch_size: int
    state_label: int
    severity: float
    days_to_symptoms: float
    scene_id: str = "scene"

    @property
    def half_size(self) -> int:
        return self.patch_size // 2


def extract_patch_with_padding(
    cube: NDArray[np.float32],  # [B, H, W]
    center_r: int,
    center_c: int,
    patch_size: int = 11,
) -> NDArray[np.float32]:
    """Extract a 3D patch of shape [B, patch_size, patch_size] centered on (center_r, center_c).

    Uses reflection padding if the patch exceeds raster bounds.
    """
    b, h, w = cube.shape
    half = patch_size // 2

    r_min = center_r - half
    r_max = center_r + half + 1
    c_min = center_c - half
    c_max = center_c + half + 1

    # Check if interior without padding
    if 0 <= r_min and r_max <= h and 0 <= c_min and c_max <= w:
        return cube[:, r_min:r_max, c_min:c_max]

    # Border case: apply reflection padding
    pad_top = max(0, -r_min)
    pad_bottom = max(0, r_max - h)
    pad_left = max(0, -c_min)
    pad_right = max(0, c_max - w)

    # Pad cube along spatial dimensions
    padded = np.pad(
        cube,
        ((0, 0), (pad_top, pad_bottom), (pad_left, pad_right)),
        mode="reflect",
    )

    r_start_p = r_min + pad_top
    c_start_p = c_min + pad_left

    return padded[:, r_start_p : r_start_p + patch_size, c_start_p : c_start_p + patch_size]


def build_patch_index(
    state_mask: NDArray[np.uint8],  # [H, W]
    severity_mask: NDArray[np.float32],  # [H, W]
    days_to_symptoms: NDArray[np.float32],  # [H, W]
    farm_mask: NDArray[np.bool_],  # [H, W]
    patch_size: int = 11,
    stride: int = 2,
    scene_id: str = "farm_001",
    balanced_sampling: bool = True,
    samples_per_class: int = 250,
    seed: int = 42,
) -> list[PatchSpec]:
    """Sample valid patch center indices across the farm.

    Optionally applies class-balanced sampling across 0=healthy, 1=pre-symptomatic, 2=diseased.
    """
    rng = np.random.default_rng(seed)
    h, w = state_mask.shape

    candidates: dict[int, list[PatchSpec]] = {0: [], 1: [], 2: []}

    for r in range(0, h, stride):
        for c in range(0, w, stride):
            if not farm_mask[r, c]:
                continue
            st = int(state_mask[r, c])
            if st not in (0, 1, 2):
                continue
            sev = float(severity_mask[r, c])
            days = float(days_to_symptoms[r, c]) if not np.isnan(days_to_symptoms[r, c]) else -1.0

            spec = PatchSpec(
                center_r=r,
                center_c=c,
                patch_size=patch_size,
                state_label=st,
                severity=sev,
                days_to_symptoms=days,
                scene_id=scene_id,
            )
            candidates[st].append(spec)

    if not balanced_sampling:
        all_specs: list[PatchSpec] = []
        for cls_list in candidates.values():
            all_specs.extend(cls_list)
        return all_specs

    # Class-balanced sampling
    balanced: list[PatchSpec] = []
    for st, specs in candidates.items():
        if len(specs) == 0:
            continue
        n_take = min(len(specs), samples_per_class)
        chosen = rng.choice(specs, size=n_take, replace=False)
        balanced.extend(chosen)

    return balanced


def save_patch_index_npz(specs: list[PatchSpec], path: str | Path) -> Path:
    """Save patch index specs to disk as a compact NumPy array archive."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    centers_r = np.array([s.center_r for s in specs], dtype=np.int32)
    centers_c = np.array([s.center_c for s in specs], dtype=np.int32)
    patch_sizes = np.array([s.patch_size for s in specs], dtype=np.int32)
    labels = np.array([s.state_label for s in specs], dtype=np.uint8)
    severities = np.array([s.severity for s in specs], dtype=np.float32)
    days = np.array([s.days_to_symptoms for s in specs], dtype=np.float32)
    scene_ids = np.array([s.scene_id for s in specs])

    np.savez_compressed(
        p,
        centers_r=centers_r,
        centers_c=centers_c,
        patch_sizes=patch_sizes,
        labels=labels,
        severities=severities,
        days=days,
        scene_ids=scene_ids,
    )
    return p
