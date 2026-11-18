"""Model training, optimization, losses, metrics, and evaluation."""

from terraspectra.training.callbacks import (
    Callback,
    EarlyStoppingCallback,
    ModelCheckpointCallback,
)
from terraspectra.training.ema import ModelEMA
from terraspectra.training.evaluate import (
    compute_spectral_signatures,
    generate_evaluation_report,
    save_prediction_geotiff,
    windowed_scene_predict,
)
from terraspectra.training.losses import (
    DiceLoss,
    FocalLoss,
    WeightedCrossEntropyLoss,
    compute_class_weights,
)
from terraspectra.training.lr_finder import LRRangeFinder
from terraspectra.training.metrics import (
    ConfusionMatrix,
    MetricCollection,
    macro_f1,
    mean_iou,
    per_class_f1,
    precision_recall_f1,
)
from terraspectra.training.sampler import get_weighted_sampler
from terraspectra.training.tracking import (
    CheckpointRegistry,
    ExperimentTracker,
    generate_results_table,
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
    "ModelEMA",
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
    "get_weighted_sampler",
    "LRRangeFinder",
    "ExperimentTracker",
    "CheckpointRegistry",
    "generate_results_table",
    "windowed_scene_predict",
    "save_prediction_geotiff",
    "compute_spectral_signatures",
    "generate_evaluation_report",
    "Trainer",
    "configure_optimizers",
    "get_cosine_schedule_with_warmup",
]
