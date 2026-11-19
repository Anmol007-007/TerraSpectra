"""PyTorch DataLoader factory with multi-worker prefetch, auto-tuning, and memory pinning."""

from __future__ import annotations

import os
import sys
from typing import Any

try:
    import torch
    from torch.utils.data import DataLoader, Dataset
except ImportError:
    torch = None  # type: ignore[assignment]
    DataLoader = object  # type: ignore[misc,assignment]
    Dataset = object  # type: ignore[misc,assignment]

from terraspectra.data.dataset import custom_collate_fn, seed_worker


def tune_optimal_num_workers(requested: int = -1) -> int:
    """Determine optimal DataLoader worker count based on platform and CPU cores.

    Args:
        requested: Requested worker count. If -1, automatically tunes.

    Returns:
        Optimal integer worker count.
    """
    if requested >= 0:
        return requested

    # On Windows, multiprocessing spawn has high pickling overhead
    if sys.platform == "win32":
        return 0

    cpu_cores = os.cpu_count() or 1
    # Cap at 4 workers to prevent thread contention with PyTorch BLAS
    return min(4, max(1, cpu_cores // 2))


def build_dataloader(
    dataset: Any,
    batch_size: int = 64,
    shuffle: bool = True,
    num_workers: int = -1,
    pin_memory: bool | None = None,
    drop_last: bool = False,
    persistent_workers: bool | None = None,
    sampler: Any = None,
) -> Any:
    """Build tuned PyTorch DataLoader for 3D hyperspectral patch training and evaluation.

    Args:
        dataset: Target Dataset.
        batch_size: Mini-batch size.
        shuffle: Whether to shuffle each epoch (ignored if sampler is provided).
        num_workers: Background subprocess worker count (-1 for auto-tuning).
        pin_memory: Fast host-to-GPU page-locked memory transfer (auto-detected if None).
        drop_last: Drop incomplete final batch.
        persistent_workers: Keep worker processes alive across epochs.
        sampler: Optional custom sampler (e.g. WeightedRandomSampler).

    Returns:
        Configured PyTorch DataLoader.
    """
    tuned_workers = tune_optimal_num_workers(num_workers)

    if pin_memory is None:
        pin_memory = torch is not None and torch.cuda.is_available()

    if persistent_workers is None:
        persistent_workers = tuned_workers > 0

    if torch is None:
        # Lightweight Python fallback iterator for environments without PyTorch installed
        class _SimpleLoader:
            def __init__(self, ds: Any, b_sz: int, shuf: bool, drop: bool) -> None:
                self.ds = ds
                self.b_sz = b_sz
                self.shuf = shuf
                self.drop = drop

            def __iter__(self) -> Any:
                indices = list(range(len(self.ds)))
                if self.shuf:
                    import random
                    random.shuffle(indices)
                for i in range(0, len(indices), self.b_sz):
                    batch_idx = indices[i : i + self.b_sz]
                    if self.drop and len(batch_idx) < self.b_sz:
                        continue
                    samples = [self.ds[j] for j in batch_idx]
                    yield custom_collate_fn(samples)

            def __len__(self) -> int:
                n = len(self.ds)
                return n // self.b_sz if self.drop else (n + self.b_sz - 1) // self.b_sz

        return _SimpleLoader(dataset, batch_size, shuffle, drop_last)

    loader_kwargs: dict[str, Any] = {
        "dataset": dataset,
        "batch_size": batch_size,
        "num_workers": tuned_workers,
        "pin_memory": pin_memory,
        "drop_last": drop_last,
        "collate_fn": custom_collate_fn,
        "worker_init_fn": seed_worker,
    }

    if sampler is not None:
        loader_kwargs["sampler"] = sampler
    else:
        loader_kwargs["shuffle"] = shuffle

    if tuned_workers > 0:
        loader_kwargs["persistent_workers"] = persistent_workers

    return DataLoader(**loader_kwargs)
