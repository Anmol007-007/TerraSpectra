"""Unit tests for seed, timer, device selection, and hashing utilities."""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np

from terraspectra.core.device import get_device_info, select_device
from terraspectra.core.hashing import hash_dict, hash_file
from terraspectra.core.seed import seed_everything
from terraspectra.core.timing import Timer, timeit


def test_seed_everything_deterministic() -> None:
    """Test seed_everything enforces reproducibility in numpy."""
    seed_everything(42)
    a = np.random.rand(5)
    seed_everything(42)
    b = np.random.rand(5)
    np.testing.assert_allclose(a, b)


def test_timer_context_manager() -> None:
    """Test Timer accurately records elapsed wall-clock time."""
    with Timer("sleep_test") as t:
        time.sleep(0.02)
    assert t.elapsed >= 0.015


def test_timeit_decorator() -> None:
    """Test timeit decorator preserves return value."""

    @timeit
    def square(n: int) -> int:
        return n * n

    assert square(9) == 81


def test_select_device_fallback() -> None:
    """Test device selection handles CPU correctly."""
    dev = select_device("cpu")
    assert dev == "cpu"
    info = get_device_info()
    assert "device" in info


def test_hashing_utilities(tmp_path: Path) -> None:
    """Test hash_file and hash_dict utilities."""
    f = tmp_path / "sample.txt"
    f.write_text("terraspectra-test")
    h1 = hash_file(f)
    assert len(h1) == 64

    d1 = {"a": 1, "b": 2}
    d2 = {"b": 2, "a": 1}
    assert hash_dict(d1) == hash_dict(d2)
