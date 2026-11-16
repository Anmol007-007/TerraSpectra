"""Training callbacks including early stopping and model checkpointing."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from terraspectra.training.trainer import Trainer

logger = logging.getLogger(__name__)


class Callback:
    """Base callback interface with lifecycle hooks for training."""

    def on_train_begin(self, trainer: Trainer) -> None:
        """Called before the first training epoch begins."""

    def on_train_end(self, trainer: Trainer) -> None:
        """Called after training concludes."""

    def on_epoch_begin(self, trainer: Trainer, epoch: int) -> None:
        """Called at the start of each epoch."""

    def on_epoch_end(self, trainer: Trainer, epoch: int, metrics: dict[str, Any]) -> None:
        """Called at the end of each epoch after validation."""

    def on_batch_end(self, trainer: Trainer, batch_idx: int, loss: float) -> None:
        """Called after each training mini-batch step."""


class EarlyStoppingCallback(Callback):
    """Halts training when a monitored validation metric ceases to improve.

    Args:
        monitor: Metric key to monitor (e.g. 'val_macro_f1' or 'val_loss').
        patience: Number of epochs with no improvement before stopping.
        mode: 'max' for metrics to maximize (F1, mIoU), 'min' for loss.
        min_delta: Minimum change in monitored metric to qualify as improvement.
    """

    def __init__(
        self,
        monitor: str = "val_macro_f1",
        patience: int = 10,
        mode: str = "max",
        min_delta: float = 1e-4,
    ) -> None:
        self.monitor = monitor
        self.patience = patience
        self.mode = mode
        self.min_delta = min_delta
        self.best_value: Optional[float] = None
        self.counter = 0

    def on_train_begin(self, trainer: Trainer) -> None:
        self.best_value = -float("inf") if self.mode == "max" else float("inf")
        self.counter = 0

    def on_epoch_end(self, trainer: Trainer, epoch: int, metrics: dict[str, Any]) -> None:
        current = metrics.get(self.monitor)
        if current is None:
            return

        improved = False
        if self.mode == "max":
            if self.best_value is None or current > self.best_value + self.min_delta:
                improved = True
        else:
            if self.best_value is None or current < self.best_value - self.min_delta:
                improved = True

        if improved:
            self.best_value = current
            self.counter = 0
            logger.info("EarlyStopping: %s improved to %.4f at epoch %d", self.monitor, current, epoch)
        else:
            self.counter += 1
            logger.info(
                "EarlyStopping: %s did not improve (best: %.4f, current: %.4f). Counter: %d/%d",
                self.monitor,
                self.best_value or 0.0,
                current,
                self.counter,
                self.patience,
            )
            if self.counter >= self.patience:
                logger.info("EarlyStopping: Patience of %d epochs reached. Halting training.", self.patience)
                trainer.stop_training = True


class ModelCheckpointCallback(Callback):
    """Persists model checkpoint whenever the monitored validation metric improves."""

    def __init__(
        self,
        filepath: str | Path,
        monitor: str = "val_macro_f1",
        mode: str = "max",
    ) -> None:
        self.filepath = Path(filepath)
        self.monitor = monitor
        self.mode = mode
        self.best_value: Optional[float] = None

    def on_train_begin(self, trainer: Trainer) -> None:
        self.best_value = -float("inf") if self.mode == "max" else float("inf")
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

    def on_epoch_end(self, trainer: Trainer, epoch: int, metrics: dict[str, Any]) -> None:
        current = metrics.get(self.monitor)
        if current is None:
            return

        improved = False
        if self.mode == "max":
            if self.best_value is None or current > self.best_value:
                improved = True
        else:
            if self.best_value is None or current < self.best_value:
                improved = True

        if improved:
            self.best_value = current
            trainer.save_checkpoint(self.filepath, epoch=epoch, metrics=metrics)
            logger.info(
                "Saved best checkpoint to %s (epoch %d, %s: %.4f)",
                self.filepath,
                epoch,
                self.monitor,
                current,
            )
