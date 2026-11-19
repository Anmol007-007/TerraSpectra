"""Full PyTorch Trainer implementation with AMP, cosine schedule, clipping, and callbacks."""

from __future__ import annotations

import logging
import math
from pathlib import Path
from typing import Any, Callable, Optional, Sequence

import torch
import torch.nn as nn
from torch import Tensor
from torch.optim import AdamW, Optimizer
from torch.optim.lr_scheduler import LambdaLR
from torch.utils.data import DataLoader

from terraspectra.core.device import select_device
from terraspectra.training.callbacks import Callback
from terraspectra.training.losses import FocalLoss
from terraspectra.training.metrics import MetricCollection

logger = logging.getLogger(__name__)


def configure_optimizers(
    model: nn.Module,
    lr: float = 3e-4,
    weight_decay: float = 1e-2,
) -> Optimizer:
    """Create AdamW optimizer with weight decay excluded from bias and 1D normalization weights."""
    decay_params: list[nn.Parameter] = []
    no_decay_params: list[nn.Parameter] = []

    for name, param in model.named_parameters():
        if not param.requires_grad:
            continue
        if param.ndim <= 1 or name.endswith(".bias"):
            no_decay_params.append(param)
        else:
            decay_params.append(param)

    optim_groups = [
        {"params": decay_params, "weight_decay": weight_decay},
        {"params": no_decay_params, "weight_decay": 0.0},
    ]
    return AdamW(optim_groups, lr=lr)


def get_cosine_schedule_with_warmup(
    optimizer: Optimizer,
    num_warmup_steps: int,
    num_training_steps: int,
    min_lr_ratio: float = 0.05,
) -> LambdaLR:
    """Create a learning rate scheduler with linear warmup and cosine decay."""

    def lr_lambda(current_step: int) -> float:
        if current_step < num_warmup_steps:
            return float(current_step) / float(max(1, num_warmup_steps))
        progress = float(current_step - num_warmup_steps) / float(
            max(1, num_training_steps - num_warmup_steps)
        )
        cosine_decay = 0.5 * (1.0 + math.cos(math.pi * progress))
        return min_lr_ratio + (1.0 - min_lr_ratio) * cosine_decay

    return LambdaLR(optimizer, lr_lambda)


class Trainer:
    """End-to-end trainer for 3D hyperspectral deep learning models."""

    def __init__(
        self,
        model: nn.Module,
        loss_fn: Optional[nn.Module] = None,
        optimizer: Optional[Optimizer] = None,
        scheduler: Optional[Any] = None,
        device: Optional[torch.device | str] = None,
        callbacks: Optional[Sequence[Callback]] = None,
        grad_clip_norm: float = 1.0,
        use_amp: bool = True,
        amp_dtype: str | torch.dtype = "float16",
        gradient_accumulation_steps: int = 1,
        channels_last_3d: bool = False,
        num_classes: int = 3,
    ) -> None:
        self.device = torch.device(device) if device is not None else select_device()
        self.model = model.to(self.device)
        self.loss_fn = loss_fn if loss_fn is not None else FocalLoss()
        self.loss_fn = self.loss_fn.to(self.device)
        self.optimizer = optimizer if optimizer is not None else configure_optimizers(self.model)
        self.scheduler = scheduler
        self.callbacks = list(callbacks or [])
        self.grad_clip_norm = grad_clip_norm
        self.gradient_accumulation_steps = max(1, gradient_accumulation_steps)
        self.channels_last_3d = channels_last_3d
        self.num_classes = num_classes

        # Mixed precision support (enabled when CUDA is active and requested)
        self.use_amp = use_amp and (self.device.type == "cuda")
        if isinstance(amp_dtype, str):
            self.amp_dtype = (
                torch.bfloat16
                if "bfloat" in amp_dtype.lower() or "bf16" in amp_dtype.lower()
                else torch.float16
            )
        else:
            self.amp_dtype = amp_dtype
        self.scaler = torch.amp.GradScaler("cuda", enabled=self.use_amp)

        self.metrics = MetricCollection(
            num_classes=num_classes,
            class_names=["healthy", "pre_symptomatic", "diseased"],
        )
        self.stop_training = False
        self.history: list[dict[str, Any]] = []

    def _extract_batch_inputs(self, batch: Any) -> tuple[Tensor, Tensor]:
        """Extract inputs and targets from various DataLoader output formats."""
        if isinstance(batch, dict):
            # Keys from custom_collate_fn: 'patches' and 'states'
            x = batch.get("patches", batch.get("patch"))
            y = batch.get("states", batch.get("state"))
        elif isinstance(batch, (tuple, list)):
            x, y = batch[0], batch[1]
        else:
            raise TypeError(f"Unsupported batch type: {type(batch)}")

        if not isinstance(x, Tensor) or not isinstance(y, Tensor):
            x = torch.as_tensor(x, dtype=torch.float32)
            y = torch.as_tensor(y, dtype=torch.int64)

        return x.to(self.device, non_blocking=True), y.to(self.device, non_blocking=True)

    def train_epoch(self, train_loader: DataLoader[Any], epoch: int) -> dict[str, float]:
        """Execute one complete training epoch."""
        self.model.train()
        self.metrics.reset()
        total_loss = 0.0
        num_batches = 0
        self.optimizer.zero_grad()

        total_iterations = len(train_loader)

        for batch_idx, batch in enumerate(train_loader):
            x, y = self._extract_batch_inputs(batch)
            if self.channels_last_3d and hasattr(torch, "channels_last_3d") and x.ndim == 5:
                x = x.to(memory_format=torch.channels_last_3d)

            with torch.amp.autocast(
                device_type=self.device.type,
                dtype=getattr(self, "amp_dtype", torch.float16),
                enabled=self.use_amp,
            ):
                out = self.model(x)
                logits = out["logits"] if isinstance(out, dict) else out
                raw_loss = self.loss_fn(logits, y)
                scaled_loss = raw_loss / self.gradient_accumulation_steps

            if self.use_amp:
                self.scaler.scale(scaled_loss).backward()
            else:
                scaled_loss.backward()

            is_accum_step = (
                (batch_idx + 1) % self.gradient_accumulation_steps == 0
                or (batch_idx + 1) == total_iterations
            )

            if is_accum_step:
                if self.use_amp:
                    if self.grad_clip_norm > 0:
                        self.scaler.unscale_(self.optimizer)
                        nn.utils.clip_grad_norm_(self.model.parameters(), self.grad_clip_norm)
                    self.scaler.step(self.optimizer)
                    self.scaler.update()
                else:
                    if self.grad_clip_norm > 0:
                        nn.utils.clip_grad_norm_(self.model.parameters(), self.grad_clip_norm)
                    self.optimizer.step()

                self.optimizer.zero_grad()

                if self.scheduler is not None:
                    self.scheduler.step()

            loss_val = float(raw_loss.item())
            total_loss += loss_val
            num_batches += 1
            self.metrics.update(logits, y)

            for cb in self.callbacks:
                cb.on_batch_end(self, batch_idx, loss_val)

        train_metrics = self.metrics.compute()
        avg_loss = total_loss / max(num_batches, 1)
        train_metrics["loss"] = round(avg_loss, 4)
        return train_metrics

    @torch.no_grad()
    def validate(self, val_loader: DataLoader[Any]) -> dict[str, Any]:
        """Execute validation evaluation pass."""
        self.model.eval()
        self.metrics.reset()
        total_loss = 0.0
        num_batches = 0

        for batch in val_loader:
            x, y = self._extract_batch_inputs(batch)
            with torch.amp.autocast(device_type=self.device.type, enabled=self.use_amp):
                out = self.model(x)
                logits = out["logits"] if isinstance(out, dict) else out
                loss = self.loss_fn(logits, y)

            total_loss += float(loss.item())
            num_batches += 1
            self.metrics.update(logits, y)

        val_metrics = self.metrics.compute()
        avg_loss = total_loss / max(num_batches, 1)
        val_metrics["loss"] = round(avg_loss, 4)
        return val_metrics

    def fit(
        self,
        train_loader: DataLoader[Any],
        val_loader: Optional[DataLoader[Any]] = None,
        epochs: int = 20,
    ) -> list[dict[str, Any]]:
        """Run complete model training lifecycle across specified number of epochs."""
        for cb in self.callbacks:
            cb.on_train_begin(self)

        self.history = []

        for epoch in range(1, epochs + 1):
            if self.stop_training:
                logger.info("Early stopping triggered. Terminating fit loop.")
                break

            for cb in self.callbacks:
                cb.on_epoch_begin(self, epoch)

            train_metrics = self.train_epoch(train_loader, epoch)
            epoch_log: dict[str, Any] = {"epoch": epoch}

            for k, v in train_metrics.items():
                epoch_log[f"train_{k}"] = v

            if val_loader is not None:
                val_metrics = self.validate(val_loader)
                for k, v in val_metrics.items():
                    epoch_log[f"val_{k}"] = v

            self.history.append(epoch_log)

            logger.info(
                "Epoch %d/%d - train_loss: %.4f - train_f1: %.4f - val_f1: %s",
                epoch,
                epochs,
                epoch_log.get("train_loss", 0.0),
                epoch_log.get("train_macro_f1", 0.0),
                str(epoch_log.get("val_macro_f1", "N/A")),
            )

            for cb in self.callbacks:
                cb.on_epoch_end(self, epoch, epoch_log)

        for cb in self.callbacks:
            cb.on_train_end(self)

        return self.history

    def save_checkpoint(
        self,
        filepath: str | Path,
        epoch: int,
        metrics: Optional[dict[str, Any]] = None,
    ) -> None:
        """Save training state checkpoint."""
        p = Path(filepath)
        p.parent.mkdir(parents=True, exist_ok=True)
        checkpoint = {
            "epoch": epoch,
            "model_state_dict": self.model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "metrics": metrics or {},
        }
        if self.scheduler is not None:
            checkpoint["scheduler_state_dict"] = self.scheduler.state_dict()
        torch.save(checkpoint, p)

    def load_checkpoint(self, filepath: str | Path) -> dict[str, Any]:
        """Restore training state from a checkpoint file."""
        p = Path(filepath)
        checkpoint = torch.load(p, map_location=self.device)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        if self.scheduler is not None and "scheduler_state_dict" in checkpoint:
            self.scheduler.load_state_dict(checkpoint["scheduler_state_dict"])
        return checkpoint
