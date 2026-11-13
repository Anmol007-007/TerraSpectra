"""Spatial windowing utilities for memory-safe chunked raster I/O.

Allows streaming tiles across multi-gigabyte scenes without full-cube RAM exhaustion.
"""

from __future__ import annotations

import math
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Iterator

import numpy as np


@dataclass(frozen=True)
class Window:
    """2D spatial window defining sub-region bounds."""

    row_off: int
    col_off: int
    height: int
    width: int

    @property
    def slice_2d(self) -> tuple[slice, slice]:
        """Return Python slices for 2D array indexing [height, width]."""
        return slice(self.row_off, self.row_off + self.height), slice(
            self.col_off, self.col_off + self.width
        )

    @property
    def slice_3d(self) -> tuple[slice, slice, slice]:
        """Return Python slices for 3D array indexing [bands, height, width]."""
        return (
            slice(None),
            slice(self.row_off, self.row_off + self.height),
            slice(self.col_off, self.col_off + self.width),
        )


def iter_blocks(
    rows: int,
    cols: int,
    block_h: int = 128,
    block_w: int = 128,
) -> Iterator[Window]:
    """Iterate contiguous non-overlapping tile blocks covering the raster."""
    for r in range(0, rows, block_h):
        h = min(block_h, rows - r)
        for c in range(0, cols, block_w):
            w = min(block_w, cols - c)
            yield Window(row_off=r, col_off=c, height=h, width=w)


def iter_overlapping_windows(
    rows: int,
    cols: int,
    tile_size: int = 256,
    overlap: int = 32,
) -> Iterator[Window]:
    """Iterate overlapping windows across the scene with designated stride."""
    stride = tile_size - overlap
    if stride <= 0:
        raise ValueError(f"tile_size ({tile_size}) must exceed overlap ({overlap})")

    r_steps = max(1, math.ceil((rows - overlap) / stride))
    c_steps = max(1, math.ceil((cols - overlap) / stride))

    for ri in range(r_steps):
        r_off = ri * stride
        h = min(tile_size, rows - r_off)
        for ci in range(c_steps):
            c_off = ci * stride
            w = min(tile_size, cols - c_off)
            yield Window(row_off=r_off, col_off=c_off, height=h, width=w)


def estimate_cube_memory_mb(bands: int, rows: int, cols: int, dtype_bytes: int = 4) -> float:
    """Calculate RAM in megabytes needed to hold a full or windowed raster."""
    return (bands * rows * cols * dtype_bytes) / (1024.0 * 1024.0)


def auto_chunk_size(
    bands: int,
    rows: int,
    cols: int,
    ram_budget_mb: float = 256.0,
    dtype_bytes: int = 4,
) -> tuple[int, int]:
    """Calculate maximum square spatial window size that fits within RAM budget."""
    total_needed = estimate_cube_memory_mb(bands, rows, cols, dtype_bytes)
    if total_needed <= ram_budget_mb:
        return (rows, cols)

    # Max pixels per slice: budget / (bands * dtype_bytes)
    budget_bytes = ram_budget_mb * 1024.0 * 1024.0
    max_pixels = budget_bytes / (bands * dtype_bytes)
    side = int(math.floor(math.sqrt(max_pixels)))
    side = max(32, min(side, rows, cols))
    return (side, side)


class WindowLRUCache:
    """Small Least-Recently-Used (LRU) memory cache for pre-fetched raster windows."""

    def __init__(self, maxsize: int = 16) -> None:
        self.maxsize = maxsize
        self._cache: OrderedDict[tuple[int, int, int, int], np.ndarray] = OrderedDict()

    def get(self, win: Window) -> np.ndarray | None:
        key = (win.row_off, win.col_off, win.height, win.width)
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        return None

    def put(self, win: Window, data: np.ndarray) -> None:
        key = (win.row_off, win.col_off, win.height, win.width)
        self._cache[key] = data
        if len(self._cache) > self.maxsize:
            self._cache.popitem(last=False)

    def clear(self) -> None:
        self._cache.clear()
