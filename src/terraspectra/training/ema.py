"""Exponential Moving Average (EMA) of model parameters for training stabilization."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

import torch
import torch.nn as nn


class ModelEMA:
    """Maintains an exponential moving average of model parameters.

    EMA smooths out noisy SGD trajectories and provides improved generalization,
    particularly on imbalanced classification tasks.

    Formula:
        shadow_weight = decay * shadow_weight + (1 - decay) * model_weight
    """

    def __init__(self, model: nn.Module, decay: float = 0.999) -> None:
        """Initialize ModelEMA with target model and decay rate.

        Args:
            model: PyTorch module whose parameters will be tracked.
            decay: Smoothing coefficient, typically in [0.99, 0.9999].
        """
        self.decay = decay
        self.shadow: dict[str, torch.Tensor] = {}
        self.backup: dict[str, torch.Tensor] = {}

        for name, param in model.named_parameters():
            if param.requires_grad:
                self.shadow[name] = param.data.clone().detach()

    @torch.no_grad()
    def update(self, model: nn.Module) -> None:
        """Update EMA parameters with current model weights."""
        for name, param in model.named_parameters():
            if param.requires_grad and name in self.shadow:
                new_val = (
                    self.decay * self.shadow[name]
                    + (1.0 - self.decay) * param.data.to(self.shadow[name].device)
                )
                self.shadow[name].copy_(new_val)

    def apply_shadow(self, model: nn.Module) -> None:
        """Copy shadow EMA weights into model parameters (saving backup first)."""
        self.backup = {}
        for name, param in model.named_parameters():
            if param.requires_grad and name in self.shadow:
                self.backup[name] = param.data.clone().detach()
                param.data.copy_(self.shadow[name].to(param.device))

    def restore(self, model: nn.Module) -> None:
        """Restore original parameters from backup prior to apply_shadow."""
        for name, param in model.named_parameters():
            if name in self.backup:
                param.data.copy_(self.backup[name].to(param.device))
        self.backup = {}

    def state_dict(self) -> dict[str, Any]:
        """Return serialized state dictionary."""
        return {
            "decay": self.decay,
            "shadow": {k: v.cpu() for k, v in self.shadow.items()},
        }

    def load_state_dict(self, state_dict: dict[str, Any]) -> None:
        """Load state dictionary."""
        self.decay = state_dict.get("decay", self.decay)
        shadow_dict = state_dict.get("shadow", {})
        for k, v in shadow_dict.items():
            if k in self.shadow:
                self.shadow[k].copy_(v.to(self.shadow[k].device))
            else:
                self.shadow[k] = v.clone()
