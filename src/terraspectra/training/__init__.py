"""Model training, optimization, losses, metrics, and evaluation."""

from terraspectra.training.callbacks import (
    Callback,
    EarlyStoppingCallback,
    ModelCheckpointCallback,
)
from terraspectra.training.losses import (
    DiceLoss,
    FocalLoss,
    WeightedCrossEntropyLoss,
    compute_class_weights,
)
from terraspectra.training.metrics import (
    ConfusionMatrix,
    MetricCollection,
    macro_f1,
    mean_iou,
    per_class_f1,
    precision_recall_f1,
)
from terraspectra.training.trainer import (
    Trainer,
    configure_optimizers,
    get_cosine_schedule_with_warmup,
)

__all__ = [
    "Callback",
    "EarlyStoppingCallback",
    "ModelCheckpointCallback",
    "compute_class_weights",
    "WeightedCrossEntropyLoss",
    "FocalLoss",
    "DiceLoss",
    "ConfusionMatrix",
    "MetricCollection",
    "precision_recall_f1",
    "macro_f1",
    "per_class_f1",
    "mean_iou",
    "Trainer",
    "configure_optimizers",
    "get_cosine_schedule_with_warmup",
]
