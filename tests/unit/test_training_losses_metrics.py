"""Unit tests for loss functions, evaluation metrics, and Trainer."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from terraspectra.models.cnn3d import CNN3DClassifier, CNN3DConfig
from terraspectra.training.callbacks import EarlyStoppingCallback, ModelCheckpointCallback
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


def test_class_weights_computation() -> None:
    """Test inverse frequency class weight calculation."""
    counts = [1000, 200, 50]  # Imbalanced: class 2 is rarest
    weights = compute_class_weights(counts, normalize=True)
    assert len(weights) == 3
    # Rarest class should receive largest weight
    assert weights[2] > weights[1] > weights[0]
    assert pytest.approx(float(weights.mean()), rel=1e-3) == 1.0


def test_loss_functions() -> None:
    """Test Weighted Cross-Entropy, Focal, and Dice loss functions."""
    logits = torch.randn(4, 3, requires_grad=True)
    targets = torch.tensor([0, 1, 2, 1], dtype=torch.int64)

    # Weighted Cross-Entropy
    wce = WeightedCrossEntropyLoss(weight=torch.tensor([1.0, 2.0, 5.0]))
    loss_wce = wce(logits, targets)
    assert loss_wce.item() > 0
    loss_wce.backward(retain_graph=True)

    # Focal Loss
    focal = FocalLoss(gamma=2.0)
    loss_focal = focal(logits, targets)
    assert loss_focal.item() > 0

    # Dice Loss
    dice = DiceLoss()
    loss_dice = dice(logits, targets)
    assert loss_dice.item() > 0


def test_metrics_collection() -> None:
    """Test confusion matrix and metric summary calculations."""
    metrics = MetricCollection(
        num_classes=3, class_names=["healthy", "pre_symptomatic", "diseased"]
    )
    # Perfect predictions
    preds = torch.tensor([0, 1, 2, 1, 0], dtype=torch.int64)
    targets = torch.tensor([0, 1, 2, 1, 0], dtype=torch.int64)

    metrics.update(preds, targets)
    res = metrics.compute()

    assert res["accuracy"] == 1.0
    assert res["macro_f1"] == 1.0
    assert res["mIoU"] == 1.0
    assert res["f1_healthy"] == 1.0

    # Imperfect predictions
    metrics.reset()
    imperfect_preds = torch.tensor([0, 0, 2, 1, 1], dtype=torch.int64)
    metrics.update(imperfect_preds, targets)
    res2 = metrics.compute()
    assert 0.0 < res2["accuracy"] < 1.0


def test_trainer_overfit_tiny_batch() -> None:
    """Test Trainer's ability to overfit a small batch of synthetic patches."""
    torch.manual_seed(42)

    # 8 samples, 1 channel, 16 depth, 7x7 spatial
    x = torch.randn(8, 1, 16, 7, 7)
    y = torch.tensor([0, 1, 2, 0, 1, 2, 0, 1], dtype=torch.int64)

    dataset = TensorDataset(x, y)
    loader = DataLoader(dataset, batch_size=4, shuffle=False)

    model = CNN3DClassifier(
        CNN3DConfig(
            in_channels=1,
            depth=16,
            patch_size=7,
            base_channels=8,
            num_classes=3,
            dropout=0.0,
        )
    )

    optimizer = configure_optimizers(model, lr=0.01)
    scheduler = get_cosine_schedule_with_warmup(optimizer, num_warmup_steps=2, num_training_steps=20)

    with tempfile.TemporaryDirectory() as tmp_dir:
        ckpt_path = Path(tmp_dir) / "best_model.pt"
        cb_checkpoint = ModelCheckpointCallback(filepath=ckpt_path, monitor="train_accuracy", mode="max")
        cb_early_stop = EarlyStoppingCallback(monitor="train_accuracy", patience=25, mode="max")

        trainer = Trainer(
            model=model,
            optimizer=optimizer,
            scheduler=scheduler,
            device="cpu",
            callbacks=[cb_checkpoint, cb_early_stop],
            grad_clip_norm=1.0,
            use_amp=False,
        )

        history = trainer.fit(train_loader=loader, val_loader=None, epochs=15)
        assert len(history) > 0

        # Loss should decrease across epochs
        first_loss = history[0]["train_loss"]
        final_loss = history[-1]["train_loss"]
        assert final_loss < first_loss

        # Verify checkpoint was written
        assert ckpt_path.exists()
        loaded = trainer.load_checkpoint(ckpt_path)
        assert "model_state_dict" in loaded
