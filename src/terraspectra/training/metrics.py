"""Evaluation metrics for hyperspectral crop disease classification.

Includes Confusion Matrix, Precision, Recall, Per-Class F1, Macro-F1,
Mean Intersection-over-Union (mIoU), and MetricCollection aggregator.
"""

from __future__ import annotations

from typing import Any, Optional

import torch
from torch import Tensor


class ConfusionMatrix:
    """Confusion matrix metric accumulating multiclass predictions and targets."""

    def __init__(self, num_classes: int = 3) -> None:
        self.num_classes = num_classes
        self.matrix = torch.zeros((num_classes, num_classes), dtype=torch.int64)

    def reset(self) -> None:
        """Reset accumulated confusion matrix."""
        self.matrix.zero_()

    def update(self, preds: Tensor, targets: Tensor) -> None:
        """Accumulate a batch of predictions and ground truth targets.

        Args:
            preds: Predicted class labels [B] or logits [B, C].
            targets: Target class labels [B].
        """
        if preds.ndim > 1:
            preds = preds.argmax(dim=-1)
        preds = preds.detach().cpu().to(torch.int64)
        targets = targets.detach().cpu().to(torch.int64)

        for t, p in zip(targets.view(-1), preds.view(-1)):
            if 0 <= t < self.num_classes and 0 <= p < self.num_classes:
                self.matrix[t, p] += 1

    def compute(self) -> Tensor:
        """Return the confusion matrix [num_classes, num_classes]."""
        return self.matrix.clone()


class MetricCollection:
    """Aggregates and computes complete multiclass diagnostic metrics."""

    def __init__(self, num_classes: int = 3, class_names: Optional[list[str]] = None) -> None:
        self.num_classes = num_classes
        self.class_names = class_names or [f"class_{i}" for i in range(num_classes)]
        self.cm = ConfusionMatrix(num_classes=num_classes)
        self.total_samples = 0
        self.correct_samples = 0

    def reset(self) -> None:
        """Reset all metric states."""
        self.cm.reset()
        self.total_samples = 0
        self.correct_samples = 0

    def update(self, preds: Tensor, targets: Tensor) -> None:
        """Update metrics with new batch."""
        if preds.ndim > 1:
            preds = preds.argmax(dim=-1)
        preds_cpu = preds.detach().cpu()
        targets_cpu = targets.detach().cpu()

        self.cm.update(preds_cpu, targets_cpu)
        self.correct_samples += int((preds_cpu == targets_cpu).sum().item())
        self.total_samples += int(targets_cpu.numel())

    def compute(self) -> dict[str, Any]:
        """Compute precision, recall, per-class F1, macro-F1, accuracy, and mIoU."""
        matrix = self.cm.compute().float()
        metrics: dict[str, Any] = {}

        # Overall accuracy
        acc = self.correct_samples / max(self.total_samples, 1)
        metrics["accuracy"] = round(acc, 4)

        f1_scores: list[float] = []
        ious: list[float] = []

        for c in range(self.num_classes):
            name = self.class_names[c]
            tp = matrix[c, c].item()
            fp = matrix[:, c].sum().item() - tp
            fn = matrix[c, :].sum().item() - tp

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = (
                (2.0 * precision * recall) / (precision + recall)
                if (precision + recall) > 0
                else 0.0
            )
            iou = tp / (tp + fp + fn) if (tp + fp + fn) > 0 else 0.0

            metrics[f"precision_{name}"] = round(precision, 4)
            metrics[f"recall_{name}"] = round(recall, 4)
            metrics[f"f1_{name}"] = round(f1, 4)
            metrics[f"iou_{name}"] = round(iou, 4)

            f1_scores.append(f1)
            ious.append(iou)

        metrics["macro_f1"] = round(sum(f1_scores) / max(len(f1_scores), 1), 4)
        metrics["mIoU"] = round(sum(ious) / max(len(ious), 1), 4)
        metrics["confusion_matrix"] = matrix.to(torch.int64).tolist()

        return metrics
