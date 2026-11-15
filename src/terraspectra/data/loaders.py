"""PyTorch DataLoader factory with multi-worker prefetch and memory pinning."""

from __future__ import annotations

from typing import Any

try:
    import torch
    from torch.utils.data import DataLoader, Dataset
except ImportError:
    torch = None  # type: ignore[assignment]
    DataLoader = object  # type: ignore[misc,assignment]
    Dataset = object  # type: ignore[misc,assignment]

from terraspectra.data.dataset import custom_collate_fn, seed_worker


def build_dataloader(
    dataset: Any,
    batch_size: int = 64,
    shuffle: bool = True,
    num_workers: int = 0,
    pin_memory: bool = False,
    drop_last: bool = False,
) -> Any:
    """Build tuned PyTorch DataLoader for 3D hyperspectral patch training and evaluation.

    Args:
        dataset: Target Dataset.
        batch_size: Mini-batch size.
        shuffle: Whether to shuffle each epoch.
        num_workers: Background subprocess worker count (0 for main process).
        pin_memory: Fast host-to-GPU page-locked memory transfer.
        drop_last: Drop incomplete final batch.

    Returns:
        Configured PyTorch DataLoader.
    """
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

    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=pin_memory,
        drop_last=drop_last,
        collate_fn=custom_collate_fn,
        worker_init_fn=seed_worker,
    )
