"""Learning Rate Range Finder (Smith, 2017) for optimal learning rate discovery."""

from __future__ import annotations

import math
from typing import Any, Callable, Optional

import torch
import torch.nn as nn
from torch.utils.data import DataLoader


class LRRangeFinder:
    """Finds optimal learning rate by exponentially increasing LR across iterations."""

    def __init__(
        self,
        model: nn.Module,
        optimizer: torch.optim.Optimizer,
        criterion: Callable[[torch.Tensor, torch.Tensor], torch.Tensor],
        device: torch.device | str = "cpu",
    ) -> None:
        self.model = model
        self.optimizer = optimizer
        self.criterion = criterion
        self.device = torch.device(device)
        self.history: dict[str, list[float]] = {"lr": [], "loss": []}
        self.best_loss = float("inf")

    def range_test(
        self,
        train_loader: DataLoader[Any],
        start_lr: float = 1e-7,
        end_lr: float = 1.0,
        num_iter: int = 100,
        smooth_f: float = 0.05,
        divergence_threshold: float = 4.0,
    ) -> dict[str, Any]:
        """Run range test over batches.

        Args:
            train_loader: DataLoader feeding training batches.
            start_lr: Minimum learning rate to test.
            end_lr: Maximum learning rate to test.
            num_iter: Maximum number of iterations / batches to evaluate.
            smooth_f: Exponential smoothing factor for loss curve.
            divergence_threshold: Factor above minimum loss indicating divergence.

        Returns:
            Dictionary with 'lrs', 'losses', and 'suggested_lr'.
        """
        self.history = {"lr": [], "loss": []}
        self.best_loss = float("inf")

        # Save initial model & optimizer states
        model_state = {k: v.cpu().clone() for k, v in self.model.state_dict().items()}
        optimizer_state = self.optimizer.state_dict()

        mult = (end_lr / start_lr) ** (1.0 / max(num_iter, 1))
        lr = start_lr
        for param_group in self.optimizer.param_groups:
            param_group["lr"] = lr

        self.model.train()
        self.model.to(self.device)
        iter_count = 0
        avg_loss = 0.0

        for batch in train_loader:
            if iter_count >= num_iter:
                break

            if isinstance(batch, (list, tuple)):
                inputs, targets = batch[0], batch[1]
            elif isinstance(batch, dict):
                inputs, targets = batch["input"], batch["target"]
            else:
                inputs, targets = batch

            inputs = inputs.to(self.device)
            targets = targets.to(self.device)

            self.optimizer.zero_grad()
            outputs = self.model(inputs)
            logits = outputs["logits"] if isinstance(outputs, dict) else outputs
            loss = self.criterion(logits, targets)

            # Check for NaN / Inf
            if torch.isnan(loss) or torch.isinf(loss):
                break

            loss.backward()
            self.optimizer.step()

            loss_val = float(loss.item())
            if iter_count == 0:
                avg_loss = loss_val
            else:
                avg_loss = smooth_f * loss_val + (1.0 - smooth_f) * avg_loss

            self.history["lr"].append(lr)
            self.history["loss"].append(avg_loss)

            if avg_loss < self.best_loss:
                self.best_loss = avg_loss

            if avg_loss > divergence_threshold * self.best_loss:
                # Stop early on divergence
                break

            lr *= mult
            for param_group in self.optimizer.param_groups:
                param_group["lr"] = lr

            iter_count += 1

        # Restore states
        self.model.load_state_dict(model_state)
        self.optimizer.load_state_dict(optimizer_state)

        # Suggest lr: learning rate with steepest descent gradient (min slope)
        suggested_lr = self._suggest_lr()

        return {
            "lrs": self.history["lr"],
            "losses": self.history["loss"],
            "suggested_lr": suggested_lr,
        }

    def _suggest_lr(self) -> float:
        """Find learning rate where loss decreases most rapidly."""
        losses = self.history["loss"]
        lrs = self.history["lr"]
        if len(losses) < 3:
            return lrs[0] if lrs else 1e-3

        # Compute differences
        gradients = [losses[i] - losses[i - 1] for i in range(1, len(losses))]
        min_grad_idx = int(gradients.index(min(gradients)))
        return lrs[min_grad_idx]
