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
from terraspectra.training.metrics import ConfusionMatrix, MetricCollection
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
    "Trainer",
    "configure_optimizers",
    "get_cosine_schedule_with_warmup",
]
