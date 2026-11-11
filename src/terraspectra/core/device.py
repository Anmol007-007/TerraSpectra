"""Hardware device selection and capability checks."""

from __future__ import annotations

import logging
from typing import Literal

logger = logging.getLogger(__name__)
DeviceString = Literal["cpu", "cuda", "mps"]


def select_device(preferred: str = "auto") -> str:
    """Select appropriate compute device with automatic CUDA/CPU fallback.

    Args:
        preferred: Requested device ("auto", "cuda", "cpu", "mps").

    Returns:
        Canonical device string ("cpu", "cuda", or "mps").
    """
    preferred = preferred.lower()
    try:
        import torch

        has_cuda = torch.cuda.is_available()
        has_mps = hasattr(torch.backends, "mps") and torch.backends.mps.is_available()

        if preferred == "auto":
            if has_cuda:
                device = "cuda"
            elif has_mps:
                device = "mps"
            else:
                device = "cpu"
        elif preferred == "cuda":
            if has_cuda:
                device = "cuda"
            else:
                logger.warning("CUDA requested but unavailable; falling back to CPU.")
                device = "cpu"
        elif preferred == "mps":
            if has_mps:
                device = "mps"
            else:
                logger.warning("MPS requested but unavailable; falling back to CPU.")
                device = "cpu"
        else:
            device = "cpu"

        return device
    except ImportError:
        logger.warning("PyTorch not installed; device defaulting to 'cpu'.")
        return "cpu"


def get_device_info() -> dict[str, str | int | float]:
    """Return dictionary with detailed hardware acceleration information."""
    info: dict[str, str | int | float] = {"device": select_device("auto")}
    try:
        import torch

        if torch.cuda.is_available():
            info["cuda_device_name"] = torch.cuda.get_device_name(0)
            info["cuda_device_count"] = torch.cuda.device_count()
            info["cuda_memory_gb"] = round(
                torch.cuda.get_device_properties(0).total_memory / (1024**3), 2
            )
    except Exception:
        pass
    return info
