"""Imbalanced data sampling utilities for hyperspectral crop disease classification."""

from __future__ import annotations

from typing import Optional, Sequence

import torch
from torch import Tensor
from torch.utils.data import WeightedRandomSampler

from terraspectra.training.losses import compute_class_weights


def get_weighted_sampler(
    targets: Sequence[int] | Tensor,
    num_classes: int = 3,
    num_samples: Optional[int] = None,
    replacement: bool = True,
) -> WeightedRandomSampler:
    """Create a WeightedRandomSampler that balances class representation per batch.

    Assigns each sample a weight inversely proportional to its class frequency,
    ensuring rare classes (such as 5-acre fungal blight ~0.5% of farm) are sampled
    frequently during training.

    Args:
        targets: Sequence of class labels for all samples.
        num_classes: Number of distinct classes (default: 3).
        num_samples: Number of samples to draw per epoch. Defaults to len(targets).
        replacement: Whether to sample with replacement (default: True).

    Returns:
        Configured PyTorch WeightedRandomSampler.
    """
    if isinstance(targets, Tensor):
        target_list = targets.detach().cpu().long().tolist()
    else:
        target_list = [int(t) for t in targets]

    counts = [0] * num_classes
    for t in target_list:
        if 0 <= t < num_classes:
            counts[t] += 1

    class_weights = compute_class_weights(counts, normalize=False)
    sample_weights = [float(class_weights[t]) if 0 <= t < num_classes else 0.0 for t in target_list]
    weights_tensor = torch.tensor(sample_weights, dtype=torch.double)

    total_samples = num_samples if num_samples is not None else len(target_list)

    return WeightedRandomSampler(
        weights=weights_tensor,
        num_samples=total_samples,
        replacement=replacement,
    )
