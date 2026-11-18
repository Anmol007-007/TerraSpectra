"""Command-line training script for 3D-CNN and ViT hyperspectral crop disease models."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Optional

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import yaml

from terraspectra.core.console import console
from terraspectra.core.device import select_device
from terraspectra.core.paths import ensure_dir
from terraspectra.core.seed import seed_everything
from terraspectra.core.settings import settings
from terraspectra.models.cnn3d import CNN3DClassifier, CNN3DConfig, count_parameters
from terraspectra.models.registry import model_registry
from terraspectra.training.callbacks import EarlyStoppingCallback, ModelCheckpointCallback
from terraspectra.training.ema import ModelEMA
from terraspectra.training.losses import (
    DiceLoss,
    FocalLoss,
    WeightedCrossEntropyLoss,
    compute_class_weights,
)
from terraspectra.training.sampler import get_weighted_sampler
from terraspectra.training.tracking import CheckpointRegistry, ExperimentTracker
from terraspectra.training.trainer import (
    Trainer,
    configure_optimizers,
    get_cosine_schedule_with_warmup,
)


def load_train_config(config_path: Optional[Path | str] = None) -> dict[str, Any]:
    """Load base training YAML configuration."""
    cfg_path = Path(config_path) if config_path else Path("configs/train.yaml")
    if not cfg_path.exists():
        # Fallback default configuration
        return {
            "training": {
                "batch_size": 16,
                "epochs": 10,
                "lr": 0.001,
                "min_lr": 0.00001,
                "weight_decay": 0.01,
                "warmup_epochs": 2,
                "grad_clip_norm": 1.0,
                "use_amp": False,
                "num_workers": 0,
                "seed": 42,
                "device": "auto",
            },
            "model": {
                "architecture": "cnn3d_v1",
                "in_channels": 1,
                "depth": 32,
                "patch_size": 11,
                "base_channels": 16,
                "num_classes": 3,
                "dropout": 0.1,
            },
            "loss": {
                "type": "focal",
                "focal_gamma": 2.0,
                "label_smoothing": 0.05,
                "use_class_weights": True,
            },
            "imbalance": {
                "sampler": "weighted",
                "use_ema": True,
                "ema_decay": 0.999,
            },
            "checkpoint": {
                "save_dir": "models_store",
                "monitor": "val_macro_f1",
                "mode": "max",
                "patience": 10,
            },
        }

    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
        return cfg if isinstance(cfg, dict) else {}


def create_demo_data(
    n_samples: int = 120,
    depth: int = 32,
    patch_size: int = 11,
) -> tuple[TensorDataset, TensorDataset]:
    """Generate reproducible synthetic training and validation patch datasets."""
    rng = np.random.RandomState(42)

    # Imbalanced class distribution: 75% Healthy, 20% Pre-symptomatic, 5% Diseased
    labels_raw = rng.choice([0, 1, 2], size=n_samples, p=[0.75, 0.20, 0.05])
    # Ensure at least 3 samples per class
    for c in range(3):
        labels_raw[c] = c

    # Patches [N, 1, D, H, W]
    patches = rng.randn(n_samples, 1, depth, patch_size, patch_size).astype(np.float32)

    # Inject distinctive spectral signals
    for i, lab in enumerate(labels_raw):
        if lab == 1:
            # Pre-symptomatic red-edge attenuation
            patches[i, 0, 10:18, :, :] += 0.8
        elif lab == 2:
            # Diseased necrosis across all bands
            patches[i, 0, :, :, :] += 1.5

    split_idx = int(n_samples * 0.8)

    train_x = torch.from_numpy(patches[:split_idx])
    train_y = torch.from_numpy(labels_raw[:split_idx]).long()

    val_x = torch.from_numpy(patches[split_idx:])
    val_y = torch.from_numpy(labels_raw[split_idx:]).long()

    return TensorDataset(train_x, train_y), TensorDataset(val_x, val_y)


def run_training(
    config_path: Optional[str] = None,
    epochs: Optional[int] = None,
    batch_size: Optional[int] = None,
    lr: Optional[float] = None,
    device: Optional[str] = None,
    focal_gamma: Optional[float] = None,
    use_amp: Optional[bool] = None,
    seed: Optional[int] = None,
) -> dict[str, Any]:
    """Execute complete end-to-end model training workflow."""
    cfg = load_train_config(config_path)

    # Apply CLI overrides
    t_cfg = cfg.setdefault("training", {})
    l_cfg = cfg.setdefault("loss", {})
    m_cfg = cfg.setdefault("model", {})
    i_cfg = cfg.setdefault("imbalance", {})
    c_cfg = cfg.setdefault("checkpoint", {})

    if epochs is not None:
        t_cfg["epochs"] = epochs
    if batch_size is not None:
        t_cfg["batch_size"] = batch_size
    if lr is not None:
        t_cfg["lr"] = lr
    if device is not None:
        t_cfg["device"] = device
    if focal_gamma is not None:
        l_cfg["focal_gamma"] = focal_gamma
    if use_amp is not None:
        t_cfg["use_amp"] = use_amp
    if seed is not None:
        t_cfg["seed"] = seed

    # 1. Seeding
    applied_seed = seed_everything(int(t_cfg.get("seed", 42)))
    dev_str = str(t_cfg.get("device", "auto"))
    resolved_device = select_device(dev_str)

    console.print(
        f"[bold green]🌱 Starting TerraSpectra Training[/bold green] (Device: {resolved_device}, Seed: {applied_seed})"
    )

    # 2. Experiment Tracker
    tracker = ExperimentTracker(experiment_name="terraspectra_cnn3d")
    tracker.snapshot_config(cfg)

    # 3. Data & Sampling
    depth = int(m_cfg.get("depth", 32))
    patch_size = int(m_cfg.get("patch_size", 11))
    train_dataset, val_dataset = create_demo_data(n_samples=160, depth=depth, patch_size=patch_size)

    # Class weights & sampler
    train_targets = [int(train_dataset[i][1]) for i in range(len(train_dataset))]
    class_counts = [train_targets.count(c) for c in range(3)]
    class_weights = compute_class_weights(class_counts, normalize=True, device=resolved_device)
    console.print(f"[cyan]Class Distribution in Train Split:[/cyan] {class_counts} -> Weights: {class_weights.tolist()}")

    use_weighted_sampler = i_cfg.get("sampler") == "weighted"
    if use_weighted_sampler:
        sampler = get_weighted_sampler(train_targets, num_classes=3)
        train_loader = DataLoader(
            train_dataset,
            batch_size=int(t_cfg.get("batch_size", 16)),
            sampler=sampler,
            drop_last=False,
        )
    else:
        train_loader = DataLoader(
            train_dataset,
            batch_size=int(t_cfg.get("batch_size", 16)),
            shuffle=True,
            drop_last=False,
        )

    val_loader = DataLoader(
        val_dataset,
        batch_size=int(t_cfg.get("batch_size", 16)),
        shuffle=False,
    )

    # 4. Model instantiation
    arch_name = m_cfg.get("architecture", "cnn3d_v1")
    model_cls = model_registry.get(arch_name)
    cnn_config = CNN3DConfig(
        in_channels=int(m_cfg.get("in_channels", 1)),
        depth=depth,
        patch_size=patch_size,
        base_channels=int(m_cfg.get("base_channels", 16)),
        num_classes=int(m_cfg.get("num_classes", 3)),
        dropout=float(m_cfg.get("dropout", 0.1)),
    )
    model: nn.Module = model_cls(cnn_config)
    num_params = count_parameters(model)
    console.print(f"[bold]Model Architecture:[/bold] {arch_name} ({num_params:,} parameters)")

    # 5. Metadata writing
    tracker.write_metadata(
        model_name=arch_name,
        num_parameters=num_params,
        device=str(resolved_device),
        extra={"config": cfg},
    )

    # 6. Loss function
    loss_type = l_cfg.get("type", "focal")
    label_smoothing = float(l_cfg.get("label_smoothing", 0.05))
    focal_gamma_val = float(l_cfg.get("focal_gamma", 2.0))

    if loss_type == "focal":
        loss_fn: nn.Module = FocalLoss(
            alpha=class_weights,
            gamma=focal_gamma_val,
            label_smoothing=label_smoothing,
        )
    elif loss_type == "weighted_ce":
        loss_fn = WeightedCrossEntropyLoss(weight=class_weights, label_smoothing=label_smoothing)
    elif loss_type == "dice":
        loss_fn = DiceLoss()
    else:
        loss_fn = nn.CrossEntropyLoss(label_smoothing=label_smoothing)

    # 7. Optimizer & Scheduler
    total_epochs = int(t_cfg.get("epochs", 10))
    learning_rate = float(t_cfg.get("lr", 0.001))
    weight_decay = float(t_cfg.get("weight_decay", 0.01))
    optimizer = configure_optimizers(model, lr=learning_rate, weight_decay=weight_decay)

    warmup_epochs = int(t_cfg.get("warmup_epochs", 2))
    total_steps = total_epochs * max(len(train_loader), 1)
    warmup_steps = warmup_epochs * max(len(train_loader), 1)
    scheduler = get_cosine_schedule_with_warmup(
        optimizer, num_warmup_steps=warmup_steps, num_training_steps=total_steps
    )

    # 8. Model EMA & Checkpoint Registry
    use_ema = bool(i_cfg.get("use_ema", True))
    ema_helper = ModelEMA(model, decay=float(i_cfg.get("ema_decay", 0.999))) if use_ema else None

    checkpoint_reg = CheckpointRegistry(base_dir=settings.models_dir)
    best_ckpt_path = tracker.checkpoints_dir / "best_model.pt"

    cb_checkpoint = ModelCheckpointCallback(
        filepath=best_ckpt_path,
        monitor=str(c_cfg.get("monitor", "val_macro_f1")),
        mode=str(c_cfg.get("mode", "max")),
    )
    cb_early_stop = EarlyStoppingCallback(
        monitor=str(c_cfg.get("monitor", "val_macro_f1")),
        patience=int(c_cfg.get("patience", 10)),
        mode=str(c_cfg.get("mode", "max")),
    )

    # 9. Trainer Engine
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        scheduler=scheduler,
        loss_fn=loss_fn,
        device=resolved_device,
        callbacks=[cb_checkpoint, cb_early_stop],
        grad_clip_norm=float(t_cfg.get("grad_clip_norm", 1.0)),
        use_amp=bool(t_cfg.get("use_amp", False)),
    )

    # Training Loop with tracking
    console.print(f"[bold cyan]🚀 Commencing {total_epochs} Training Epochs...[/bold cyan]")
    best_macro_f1 = -1.0

    for epoch in range(1, total_epochs + 1):
        train_metrics = trainer.train_epoch(train_loader, epoch=epoch)
        val_metrics = trainer.validate(val_loader, epoch=epoch)

        if ema_helper is not None:
            ema_helper.update(model)

        combined_metrics = {**train_metrics, **val_metrics}
        tracker.log_metrics(epoch, combined_metrics)

        current_macro_f1 = float(val_metrics.get("val_macro_f1", 0.0))
        is_best = current_macro_f1 > best_macro_f1
        if is_best:
            best_macro_f1 = current_macro_f1
            checkpoint_reg.register(
                checkpoint_path=best_ckpt_path,
                metric_name="val_macro_f1",
                metric_value=best_macro_f1,
                epoch=epoch,
                config=cfg,
                is_best=True,
            )

        console.print(
            f"Epoch {epoch:02d}/{total_epochs:02d} | "
            f"Train Loss: {train_metrics['train_loss']:.4f} Acc: {train_metrics['train_accuracy']:.4f} | "
            f"Val Loss: {val_metrics['val_loss']:.4f} Acc: {val_metrics['val_accuracy']:.4f} Macro-F1: {current_macro_f1:.4f} mIoU: {val_metrics['val_mIoU']:.4f}"
        )

        # Early stopping check
        if cb_early_stop.should_stop:
            console.print(f"[yellow]Early stopping triggered at epoch {epoch}[/yellow]")
            break

    tracker.close()
    console.print(
        f"[bold green]✅ Training Completed![/bold green] Best Macro-F1: {best_macro_f1:.4f}. Run artifacts saved to {tracker.run_dir}"
    )

    return {
        "best_macro_f1": best_macro_f1,
        "run_dir": str(tracker.run_dir),
        "best_checkpoint": str(best_ckpt_path),
    }


def main() -> None:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description="TerraSpectra 3D-CNN Model Training")
    parser.add_argument("--config", type=str, default="configs/train.yaml", help="Path to YAML config")
    parser.add_argument("--epochs", type=int, default=None, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=None, help="Batch size")
    parser.add_argument("--lr", type=float, default=None, help="Initial learning rate")
    parser.add_argument("--device", type=str, default=None, help="Target device (cpu, cuda, auto)")
    parser.add_argument("--gamma", type=float, default=None, help="Focal loss gamma parameter")
    parser.add_argument("--use-amp", action="store_true", default=None, help="Enable automatic mixed precision")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")

    args = parser.parse_args()

    run_training(
        config_path=args.config,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        device=args.device,
        focal_gamma=args.gamma,
        use_amp=args.use_amp,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
