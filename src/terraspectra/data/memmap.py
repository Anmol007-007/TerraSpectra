"""Memory-mapped array helpers for out-of-core hyperspectral cube streaming."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import numpy as np
from numpy.typing import DTypeLike

from terraspectra.core.paths import ensure_dir


def create_memmap_cube(
    file_path: str | Path,
    shape: Sequence[int],
    dtype: DTypeLike = "float32",
    fill_value: float = 0.0,
) -> np.memmap:
    """Create a new disk-backed memory-mapped array for massive hyperspectral rasters.

    Allows reading and writing multi-gigabyte cubes without exhausting process RAM.

    Args:
        file_path: Destination binary file path on disk.
        shape: Array dimensions [Bands, Height, Width] or [Height, Width].
        dtype: Data type (default float32).
        fill_value: Initial fill constant.

    Returns:
        np.memmap array in read-write ('w+') mode.
    """
    p = Path(file_path)
    ensure_dir(p.parent)

    mm = np.memmap(
        filename=str(p),
        dtype=dtype,
        mode="w+",
        shape=tuple(shape),
    )
    if fill_value != 0.0:
        mm[:] = fill_value
        mm.flush()
    return mm


def open_memmap_cube(
    file_path: str | Path,
    shape: Sequence[int],
    dtype: DTypeLike = "float32",
    mode: str = "r",
) -> np.memmap:
    """Open an existing memory-mapped hyperspectral array in read-only or read-write mode.

    Args:
        file_path: Path to binary array file on disk.
        shape: Tuple of array dimensions.
        dtype: Data type of stored array elements.
        mode: Open mode ('r' for read-only, 'r+' for read-write).

    Returns:
        np.memmap array instance.
    """
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(f"Memmap file not found: {p}")

    return np.memmap(
        filename=str(p),
        dtype=dtype,
        mode=mode,
        shape=tuple(shape),
    )
