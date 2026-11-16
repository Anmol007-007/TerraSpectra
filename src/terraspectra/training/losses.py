"""Loss functions for hyperspectral crop disease classification.

Implements Weighted Cross-Entropy, Multiclass Focal Loss, Multiclass Dice Loss,
and inverse frequency class weight computation for highly imbalanced disease labels.
"""

from __future__ import annotations

from typing import Optional, Sequence, Union

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor


def compute_class_weights(
    counts: Union[Sequence[int], np.ndarray, Tensor],
    normalize: bool = True,
    device: Optional[torch.device] = None,
) -> Tensor:
    """Compute balanced class weights inversely proportional to class frequencies.

    Formula: W_c = N_total / (N_classes * N_c)

    Args:
        counts: Number of samples in each class.
        normalize: Whether to normalize weights so their mean is 1.0.
        device: Target torch device.

    Returns:
        1D Tensor of class weights of shape [num_classes].
    """
    if isinstance(counts, Tensor):
        counts_arr = counts.cpu().numpy().astype(np.float64)
    else:
        counts_arr = np.array(counts, dtype=np.float64)

    total_samples = np.sum(counts_arr)
    num_classes = len(counts_arr)

    # Avoid zero division
    counts_clipped = np.maximum(counts_arr, 1.0)
    weights = total_samples / (num_classes * counts_clipped)

    if normalize:
        weights = weights / np.mean(weights)

    out = torch.from_numpy(weights).to(dtype=torch.float32)
    if device is not None:
        out = out.to(device)
    return out


class WeightedCrossEntropyLoss(nn.Module):
    """Cross-entropy loss with explicit class weight balancing and label smoothing."""

    def __init__(
        self,
        weight: Optional[Tensor] = None,
        label_smoothing: float = 0.05,
    ) -> None:
        super().__init__()
        self.loss_fn = nn.CrossEntropyLoss(weight=weight, label_smoothing=label_smoothing)

    def forward(self, logits: Tensor, targets: Tensor) -> Tensor:
        return self.loss_fn(logits, targets)


class FocalLoss(nn.Module):
    """Multiclass Focal Loss addressing extreme foreground-background class imbalance.

    FL(p_t) = -alpha_t * (1 - p_t)^gamma * log(p_t)
    """

    def __init__(
        self,
        alpha: Optional[Tensor] = None,
        gamma: float = 2.0,
        reduction: str = "mean",
    ) -> None:
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction

    def forward(self, logits: Tensor, targets: Tensor) -> Tensor:
        """Forward pass.

        Args:
            logits: Unnormalized network predictions [B, num_classes].
            targets: Integer class labels [B].
        """
        ce_loss = F.cross_entropy(logits, targets, reduction="none")  # [B]
        pt = torch.exp(-ce_loss)  # p_t
        focal_weight = (1.0 - pt) ** self.gamma

        if self.alpha is not None:
            alpha = self.alpha.to(logits.device)
            at = alpha[targets]
            focal_loss = at * focal_weight * ce_loss
        else:
            focal_loss = focal_weight * ce_loss

        if self.reduction == "mean":
            return focal_loss.mean()
        if self.reduction == "sum":
            return focal_loss.sum()
        return focal_loss


class DiceLoss(nn.Module):
    """Multiclass soft Dice loss for patch classification / region overlap."""

    def __init__(self, smooth: float = 1e-5, reduction: str = "mean") -> None:
        super().__init__()
        self.smooth = smooth
        self.reduction = reduction

    def forward(self, logits: Tensor, targets: Tensor) -> Tensor:
        """Forward pass.

        Args:
            logits: [B, num_classes] predictions.
            targets: [B] integer class targets.
        """
        num_classes = logits.shape[1]
        probs = F.softmax(logits, dim=1)
        targets_one_hot = F.one_hot(targets, num_classes=num_classes).float()

        dims = (0,)  # reduce over batch
        intersection = torch.sum(probs * targets_one_hot, dim=dims)
        cardinality = torch.sum(probs + targets_one_hot, dim=dims)

        dice_score = (2.0 * intersection + self.smooth) / (cardinality + self.smooth)
        dice_loss = 1.0 - dice_score

        if self.reduction == "mean":
            return dice_loss.mean()
        return dice_loss
