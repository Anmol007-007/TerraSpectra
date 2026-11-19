"""Unit tests for memory profiling, tensor calculation, and OOM retry handling."""

from __future__ import annotations

import pytest
import torch
import torch.nn as nn

from terraspectra.models.cnn3d import CNN3DClassifier, CNN3DConfig
from terraspectra.training.profiling import (
    catch_oom_and_retry,
    compute_tensor_bytes,
    estimate_max_batch_size,
    get_cpu_rss_mb,
    profile_forward_backward,
)


def test_compute_tensor_bytes() -> None:
    """Validate exact byte calculation across tensor dimensions and datatypes."""
    # float32 = 4 bytes
    assert compute_tensor_bytes((10, 10), "float32") == 400
    assert compute_tensor_bytes((224, 67, 67), "float32") == 224 * 67 * 67 * 4

    # float16 = 2 bytes
    assert compute_tensor_bytes((224, 67, 67), "float16") == 224 * 67 * 67 * 2

    # int64 = 8 bytes
    assert compute_tensor_bytes((100,), "int64") == 800


def test_estimate_max_batch_size() -> None:
    """Test dynamic batch sizing with given memory budgets."""
    # 4 GB budget for 32x11x11 patch
    bs_4gb = estimate_max_batch_size(patch_shape=(32, 11, 11), memory_budget_gb=4.0)
    assert bs_4gb >= 16

    # 8 GB budget should allow equal or greater batch size
    bs_8gb = estimate_max_batch_size(patch_shape=(32, 11, 11), memory_budget_gb=8.0)
    assert bs_8gb >= bs_4gb


def test_get_cpu_rss_mb() -> None:
    """Ensure CPU RSS returns a positive valid number."""
    rss = get_cpu_rss_mb()
    assert isinstance(rss, float)
    assert rss > 0.0


def test_catch_oom_and_retry_normal() -> None:
    """Ensure normal execution succeeds without triggering retry."""
    executed = False
    with catch_oom_and_retry(initial_batch_size=16) as state:
        executed = True

    assert executed is True
    assert state["batch_size"] == 16
    assert state["retried"] is False


def test_catch_oom_and_retry_simulated() -> None:
    """Ensure simulated CUDA OOM catches and halves batch size."""
    attempts = 0
    with catch_oom_and_retry(initial_batch_size=32) as state:
        attempts += 1
        if attempts == 1:
            # Simulate CUDA out of memory error
            raise torch.cuda.OutOfMemoryError("CUDA out of memory in test")

    assert state["batch_size"] == 16
    assert state["retried"] is True


def test_light_forward_backward_profiling() -> None:
    """Validate light forward-backward latency and memory profiler."""
    model = CNN3DClassifier(CNN3DConfig(depth=8, patch_size=5, base_channels=8, num_classes=3))
    x = torch.randn(2, 1, 8, 5, 5)
    y = torch.randint(0, 3, (2,))
    criterion = nn.CrossEntropyLoss()

    stats = profile_forward_backward(
        model=model,
        sample_input=x,
        criterion=criterion,
        target=y,
        num_runs=3,
        use_amp=False,
    )

    assert "forward_ms_avg" in stats
    assert "backward_ms_avg" in stats
    assert stats["forward_ms_avg"] > 0
    assert stats["backward_ms_avg"] > 0
