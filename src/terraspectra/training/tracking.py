"""Experiment tracking, metrics logging, artifact snapshots, and checkpoint management."""

from __future__ import annotations

import csv
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import yaml

from terraspectra.core.hashing import get_git_hash
from terraspectra.core.paths import ensure_dir
from terraspectra.core.settings import settings


class ExperimentTracker:
    """Manages experiment run directories, config snapshots, metadata, and metric logging."""

    def __init__(
        self,
        experiment_name: str = "terraspectra_training",
        run_dir: Optional[Path | str] = None,
        base_dir: Optional[Path | str] = None,
    ) -> None:
        self.experiment_name = experiment_name
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.git_hash = get_git_hash()

        if run_dir:
            self.run_dir = Path(run_dir)
        else:
            base = Path(base_dir) if base_dir else settings.reports_dir / "runs"
            short_hash = self.git_hash[:7] if self.git_hash != "unknown" else "local"
            self.run_dir = base / f"run_{self.timestamp}_{short_hash}"

        ensure_dir(self.run_dir)
        self.checkpoints_dir = ensure_dir(self.run_dir / "checkpoints")

        # CSV Logging
        self.csv_path = self.run_dir / "metrics.csv"
        self._csv_writer: Optional[csv.writer] = None
        self._csv_file: Optional[Any] = None
        self._fieldnames: list[str] = []

        # Tensorboard summary writer (optional fallback)
        self.tb_writer = self._init_tensorboard()

    def _init_tensorboard(self) -> Any:
        try:
            from torch.utils.tensorboard import SummaryWriter

            return SummaryWriter(log_dir=str(self.run_dir / "tensorboard"))
        except Exception:
            return None

    def snapshot_config(self, config_dict: dict[str, Any]) -> Path:
        """Write configuration snapshot YAML file into run directory."""
        snapshot_file = self.run_dir / "config_snapshot.yaml"
        with open(snapshot_file, "w", encoding="utf-8") as f:
            yaml.safe_dump(config_dict, f, default_flow_style=False)
        return snapshot_file

    def write_metadata(
        self,
        model_name: str,
        num_parameters: int,
        device: str,
        extra: Optional[dict[str, Any]] = None,
    ) -> Path:
        """Write execution metadata JSON into run directory."""
        metadata = {
            "experiment_name": self.experiment_name,
            "timestamp": self.timestamp,
            "git_hash": self.git_hash,
            "python_version": sys.version,
            "platform": sys.platform,
            "model_name": model_name,
            "num_parameters": num_parameters,
            "device": device,
            **(extra or {}),
        }
        metadata_file = self.run_dir / "metadata.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        return metadata_file

    def log_metrics(self, epoch: int, metrics: dict[str, Any]) -> None:
        """Log epoch metrics to CSV and Tensorboard."""
        row = {"epoch": epoch, **metrics}

        # CSV log
        write_header = not self.csv_path.exists()
        with open(self.csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(row.keys()))
            if write_header:
                writer.writeheader()
            writer.writerow(row)

        # TensorBoard log
        if self.tb_writer is not None:
            for k, v in metrics.items():
                if isinstance(v, (int, float)):
                    self.tb_writer.add_scalar(k, v, epoch)

    def close(self) -> None:
        """Flush and close active loggers."""
        if self.tb_writer is not None:
            self.tb_writer.flush()
            self.tb_writer.close()


class CheckpointRegistry:
    """Tracks model checkpoints and maintains best-model references."""

    def __init__(self, base_dir: Optional[Path | str] = None) -> None:
        self.base_dir = ensure_dir(base_dir or settings.models_dir)
        self.registry_file = self.base_dir / "checkpoint_registry.json"
        self.entries: list[dict[str, Any]] = self._load()

    def _load(self) -> list[dict[str, Any]]:
        if self.registry_file.exists():
            try:
                with open(self.registry_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else []
            except Exception:
                return []
        return []

    def _save(self) -> None:
        with open(self.registry_file, "w", encoding="utf-8") as f:
            json.dump(self.entries, f, indent=2)

    def register(
        self,
        checkpoint_path: Path | str,
        metric_name: str,
        metric_value: float,
        epoch: int,
        config: Optional[dict[str, Any]] = None,
        is_best: bool = False,
    ) -> None:
        """Register a new checkpoint in the registry."""
        src_path = Path(checkpoint_path)
        entry = {
            "checkpoint_path": str(src_path.resolve()),
            "filename": src_path.name,
            "metric_name": metric_name,
            "metric_value": metric_value,
            "epoch": epoch,
            "registered_at": datetime.now().isoformat(),
            "git_hash": get_git_hash(),
            "config": config or {},
        }
        self.entries.append(entry)
        self._save()

        if is_best:
            self.update_best_symlink(src_path)

    def update_best_symlink(self, target_checkpoint: Path) -> Path:
        """Create or update best_model.pt link/copy pointing to top checkpoint."""
        best_target = self.base_dir / "best_model.pt"
        try:
            if best_target.exists() or best_target.is_symlink():
                best_target.unlink()
            # Try symlink; on Windows fallback to file copy if privilege required
            try:
                os.symlink(target_checkpoint, best_target)
            except (OSError, NotImplementedError):
                shutil.copy2(target_checkpoint, best_target)
        except Exception:
            shutil.copy2(target_checkpoint, best_target)
        return best_target

    def get_best_checkpoint(self, metric_name: str = "val_macro_f1") -> Optional[dict[str, Any]]:
        """Return registry entry with highest metric value."""
        matching = [e for e in self.entries if e.get("metric_name") == metric_name]
        if not matching:
            return self.entries[-1] if self.entries else None
        return max(matching, key=lambda e: float(e.get("metric_value", 0.0)))


def generate_results_table(runs_dir: Optional[Path | str] = None) -> str:
    """Scan run directories and generate a markdown table of experiment results."""
    base = Path(runs_dir) if runs_dir else settings.reports_dir / "runs"
    if not base.exists():
        return "| Run ID | Date | Git Hash | Epochs | Macro-F1 | Accuracy | mIoU |\n|---|---|---|---|---|---|---|\n"

    rows: list[str] = [
        "| Run ID | Date | Git Hash | Epochs | Macro-F1 | Accuracy | mIoU |",
        "|---|---|---|---|---|---|---|",
    ]

    for run_folder in sorted(base.glob("run_*")):
        meta_file = run_folder / "metadata.json"
        csv_file = run_folder / "metrics.csv"
        run_id = run_folder.name

        date = "-"
        git_hash = "-"
        if meta_file.exists():
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    m = json.load(f)
                    date = m.get("timestamp", "-")
                    git_hash = m.get("git_hash", "-")[:7]
            except Exception:
                pass

        epochs = "-"
        macro_f1 = "-"
        acc = "-"
        miou = "-"

        if csv_file.exists():
            try:
                with open(csv_file, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    all_rows = list(reader)
                    if all_rows:
                        last = all_rows[-1]
                        epochs = last.get("epoch", "-")
                        macro_f1 = str(round(float(last.get("val_macro_f1", 0.0)), 4)) if "val_macro_f1" in last else "-"
                        acc = str(round(float(last.get("val_accuracy", 0.0)), 4)) if "val_accuracy" in last else "-"
                        miou = str(round(float(last.get("val_mIoU", 0.0)), 4)) if "val_mIoU" in last else "-"
            except Exception:
                pass

        rows.append(f"| {run_id} | {date} | {git_hash} | {epochs} | {macro_f1} | {acc} | {miou} |")

    return "\n".join(rows)
