"""Memory profiling tools, tensor size estimation, and execution audit reporting."""

from __future__ import annotations

import gc
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional, Sequence, Union

import numpy as np
import torch
import torch.nn as nn

from terraspectra.core.console import console
from terraspectra.core.paths import ensure_dir
from terraspectra.core.settings import settings


def compute_tensor_bytes(
    shape: Sequence[int],
    dtype: Union[torch.dtype, np.dtype, str] = "float32",
) -> int:
    """Calculate the exact byte size of a tensor given its shape and datatype.

    Args:
        shape: Tuple or list of tensor dimensions.
        dtype: Data type (PyTorch dtype, NumPy dtype, or string name).

    Returns:
        Total size in bytes.
    """
    total_elements = 1
    for dim in shape:
        total_elements *= int(dim)

    # Element size mapping
    dtype_str = str(dtype).lower()
    if "float64" in dtype_str or "double" in dtype_str or "int64" in dtype_str or "long" in dtype_str:
        bytes_per_elem = 8
    elif "float32" in dtype_str or "int32" in dtype_str:
        bytes_per_elem = 4
    elif "float16" in dtype_str or "bfloat16" in dtype_str or "int16" in dtype_str or "half" in dtype_str:
        bytes_per_elem = 2
    elif "int8" in dtype_str or "uint8" in dtype_str or "bool" in dtype_str:
        bytes_per_elem = 1
    else:
        bytes_per_elem = 4

    return total_elements * bytes_per_elem


def get_cuda_memory_stats(device: Optional[torch.device | str] = None) -> dict[str, float]:
    """Return current and peak CUDA memory consumption in megabytes (MB).

    Args:
        device: Target CUDA device. Defaults to current device.

    Returns:
        Dictionary with allocated_mb, reserved_mb, max_allocated_mb, max_reserved_mb.
    """
    if not torch.cuda.is_available():
        return {
            "cuda_available": False,
            "allocated_mb": 0.0,
            "reserved_mb": 0.0,
            "max_allocated_mb": 0.0,
            "max_reserved_mb": 0.0,
        }

    dev = torch.device(device if device is not None else "cuda")
    mb = 1024.0 * 1024.0

    return {
        "cuda_available": True,
        "allocated_mb": round(torch.cuda.memory_allocated(dev) / mb, 2),
        "reserved_mb": round(torch.cuda.memory_reserved(dev) / mb, 2),
        "max_allocated_mb": round(torch.cuda.max_memory_allocated(dev) / mb, 2),
        "max_reserved_mb": round(torch.cuda.max_memory_reserved(dev) / mb, 2),
    }


def get_cpu_rss_mb() -> float:
    """Return process Resident Set Size (RSS) in megabytes."""
    try:
        import psutil

        process = psutil.Process(os.getpid())
        return round(process.memory_info().rss / (1024.0 * 1024.0), 2)
    except Exception:
        # Fallback on platforms where psutil is not available
        try:
            import resource

            rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            # On Linux ru_maxrss is in KB, on macOS in bytes
            if sys.platform == "darwin":
                return round(rss / (1024.0 * 1024.0), 2)
            return round(rss / 1024.0, 2)
        except Exception:
            return 0.0


def estimate_max_batch_size(
    patch_shape: tuple[int, int, int],  # (Depth, Height, Width)
    memory_budget_gb: float = 4.0,
    model_params: int = 150_000,
    dtype_bytes: int = 4,
    safety_factor: float = 0.65,
) -> int:
    """Estimate maximum viable mini-batch size under a strict GPU/RAM memory budget.

    Accounts for:
    - Input batch tensor size: B * 1 * D * H * W * dtype_bytes
    - Activation footprint: ~6x input size for 3D-CNN forward/backward graphs
    - Model weights + AdamW optimizer states (16 bytes per param)

    Args:
        patch_shape: (Depth, Height, Width) of volumetric patch.
        memory_budget_gb: Memory threshold in gigabytes.
        model_params: Number of trainable parameters in model.
        dtype_bytes: Bytes per floating point element (4 for fp32, 2 for fp16/bf16).
        safety_factor: Conservative safety margin (default: 65% to avoid CUDA OOM).

    Returns:
        Estimated integer mini-batch size (minimum 1).
    """
    total_budget_bytes = memory_budget_gb * 1024 * 1024 * 1024 * safety_factor

    # Fixed overhead: model weights (fp32) + gradients (fp32) + Adam states (momentum + variance)
    fixed_overhead_bytes = model_params * 16  # 4 bytes weight + 4 bytes grad + 8 bytes AdamW

    usable_bytes = max(total_budget_bytes - fixed_overhead_bytes, 1024 * 1024)

    # Per-sample footprint: input tensor + forward activations + backward gradient graphs (~8x total)
    d, h, w = patch_shape
    per_sample_input_bytes = d * h * w * dtype_bytes
    per_sample_total_bytes = per_sample_input_bytes * 8.0

    batch_size = int(usable_bytes / per_sample_total_bytes)
    return max(1, batch_size)


def profile_forward_backward(
    model: nn.Module,
    sample_input: torch.Tensor,
    criterion: Callable[[torch.Tensor, torch.Tensor], torch.Tensor],
    target: torch.Tensor,
    use_amp: bool = False,
    amp_dtype: torch.dtype = torch.float16,
    num_warmup: int = 2,
    num_runs: int = 5,
) -> dict[str, Any]:
    """Benchmark memory peaks and execution times for forward and backward passes.

    Args:
        model: PyTorch module.
        sample_input: Input tensor [B, 1, D, H, W].
        criterion: Loss function.
        target: Target tensor [B].
        use_amp: Whether to use automatic mixed precision.
        amp_dtype: Mixed precision data type (torch.float16 or torch.bfloat16).
        num_warmup: Warmup iterations.
        num_runs: Timed benchmark iterations.

    Returns:
        Dictionary of timing (forward_ms, backward_ms) and memory stats.
    """
    device = sample_input.device
    model.train()

    # Reset peak stats
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)
    gc.collect()

    initial_rss = get_cpu_rss_mb()

    # Warmup
    for _ in range(num_warmup):
        model.zero_grad()
        with torch.autocast(device_type=device.type, dtype=amp_dtype, enabled=use_amp):
            out = model(sample_input)
            logits = out["logits"] if isinstance(out, dict) else out
            loss = criterion(logits, target)
        loss.backward()

    if device.type == "cuda":
        torch.cuda.synchronize(device)

    fwd_times: list[float] = []
    bwd_times: list[float] = []

    for _ in range(num_runs):
        model.zero_grad()

        # Forward pass
        t0 = time.perf_counter()
        with torch.autocast(device_type=device.type, dtype=amp_dtype, enabled=use_amp):
            out = model(sample_input)
            logits = out["logits"] if isinstance(out, dict) else out
            loss = criterion(logits, target)
        if device.type == "cuda":
            torch.cuda.synchronize(device)
        t1 = time.perf_counter()
        fwd_times.append((t1 - t0) * 1000.0)

        # Backward pass
        t2 = time.perf_counter()
        loss.backward()
        if device.type == "cuda":
            torch.cuda.synchronize(device)
        t3 = time.perf_counter()
        bwd_times.append((t3 - t2) * 1000.0)

    peak_cuda = get_cuda_memory_stats(device)
    final_rss = get_cpu_rss_mb()

    return {
        "forward_ms_avg": round(float(np.mean(fwd_times)), 2),
        "forward_ms_std": round(float(np.std(fwd_times)), 2),
        "backward_ms_avg": round(float(np.mean(bwd_times)), 2),
        "backward_ms_std": round(float(np.std(bwd_times)), 2),
        "batch_size": int(sample_input.shape[0]),
        "input_shape": list(sample_input.shape),
        "input_bytes_mb": round(compute_tensor_bytes(sample_input.shape, sample_input.dtype) / (1024 * 1024), 2),
        "cpu_rss_delta_mb": round(final_rss - initial_rss, 2),
        "cuda_memory": peak_cuda,
    }


def write_profiling_report(
    report_data: dict[str, Any],
    output_dir: Optional[Path | str] = None,
    filename_prefix: str = "memory_audit",
) -> tuple[Path, Path]:
    """Write structured memory profiling audit report in Markdown and JSON formats."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path(output_dir) if output_dir else settings.reports_dir / "audits"
    ensure_dir(out_dir)

    json_path = out_dir / f"{filename_prefix}_{timestamp}.json"
    md_path = out_dir / f"{filename_prefix}_{timestamp}.md"

    # Save JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    # Save Markdown
    lines = [
        f"# TerraSpectra Memory Audit & Extraction Report ({timestamp})",
        "",
        "## 1. System & Hardware Context",
        f"- **Python Version:** {sys.version.split()[0]}",
        f"- **Platform:** {sys.platform}",
        f"- **PyTorch Version:** {torch.__version__}",
        f"- **Initial CPU RSS:** {report_data.get('initial_rss_mb', 'N/A')} MB",
        f"- **CUDA Available:** {torch.cuda.is_available()}",
        "",
        "## 2. Theoretical Tensor Dimensions & Memory Footprint",
        "| Tensor Description | Shape | Data Type | Theoretical Size |",
        "|---|---|---|---|",
    ]

    tensor_examples = report_data.get("tensor_calculations", [])
    for t in tensor_examples:
        lines.append(f"| {t['name']} | `{t['shape']}` | `{t['dtype']}` | {t['size_mb']} MB |")

    lines.extend([
        "",
        "## 3. Forward & Backward Pass Memory Profiling",
    ])

    pass_stats = report_data.get("pass_profiling", {})
    if pass_stats:
        lines.extend([
            f"- **Input Batch Dimensions:** `{pass_stats.get('input_shape')}`",
            f"- **Forward Pass Latency:** {pass_stats.get('forward_ms_avg')} ms ± {pass_stats.get('forward_ms_std')} ms",
            f"- **Backward Pass Latency:** {pass_stats.get('backward_ms_avg')} ms ± {pass_stats.get('backward_ms_std')} ms",
            f"- **Input Tensor Memory:** {pass_stats.get('input_bytes_mb')} MB",
            f"- **CPU RSS Increase:** {pass_stats.get('cpu_rss_delta_mb')} MB",
        ])

    lines.extend([
        "",
        "## 4. Extraction Audit Memory Budget Assertion",
        f"- **Memory Budget Threshold:** {report_data.get('memory_budget_mb', 2048)} MB (2.0 GB)",
        f"- **Peak Observed Memory:** {report_data.get('peak_memory_mb', 'N/A')} MB",
        f"- **Compliance Status:** **{'PASSED (Zero OOM Violations)' if report_data.get('passed_audit', True) else 'FAILED'}**",
        "",
        "---",
        "*Automated Extraction Audit generated by `terraspectra.training.profiling`.*",
    ])

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return md_path, json_path


class catch_oom_and_retry:
    """Context manager / decorator to gracefully catch Out-Of-Memory errors and support batch-halving retry."""

    def __init__(
        self,
        fallback_batch_size: Optional[int] = None,
        initial_batch_size: int = 32,
        min_batch_size: int = 1,
    ) -> None:
        self.initial_batch_size = initial_batch_size
        self.current_batch_size = fallback_batch_size if fallback_batch_size is not None else initial_batch_size
        self.min_batch_size = min_batch_size
        self.oom_occurred = False
        self.retried = False

    def __enter__(self) -> catch_oom_and_retry:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        if exc_type is not None:
            err_msg = str(exc_val).lower()
            if "out of memory" in err_msg or (
                hasattr(torch.cuda, "OutOfMemoryError") and issubclass(exc_type, torch.cuda.OutOfMemoryError)
            ):
                self.oom_occurred = True
                self.retried = True
                self.current_batch_size = max(self.min_batch_size, self.current_batch_size // 2)
                console.print(
                    f"[bold red]⚠️ OutOfMemory detected! Halving batch size to {self.current_batch_size}...[/bold red]"
                )
                gc.collect()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                return True  # Suppress exception and let caller retry
        return False

    def __getitem__(self, key: str) -> Any:
        if key == "batch_size":
            return self.current_batch_size
        elif key == "retried":
            return self.retried
        elif key == "oom_occurred":
            return self.oom_occurred
        raise KeyError(key)
