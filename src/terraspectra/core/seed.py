"""Reproducibility utilities: seed all pseudorandom number generators."""

from __future__ import annotations

import os
import random
from typing import Any

import numpy as np


def seed_everything(seed: int = 42, deterministic_torch: bool = True) -> int:
    """Seed Python random, NumPy, and PyTorch (if available) for reproducibility.

    Args:
        seed: Integer seed value.
        deterministic_torch: If True, set torch.backends.cudnn.deterministic.

    Returns:
        The seed integer applied.
    """
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    np.random.seed(seed)

    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed(seed)
            torch.cuda.manual_seed_all(seed)
        if deterministic_torch:
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
    except ImportError:
        pass

    return seed
