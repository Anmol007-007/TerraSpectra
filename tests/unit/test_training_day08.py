"""Unit tests for Day 8 training script, imbalance handling, tracking, and evaluation."""

from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
import pytest
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from terraspectra.models.cnn3d import CNN3DClassifier, CNN3DConfig
from terraspectra.training.ema import ModelEMA
from terraspectra.training.evaluate import (
    compute_spectral_signatures,
    generate_evaluation_report,
    save_prediction_geotiff,
    windowed_scene_predict,
)
from terraspectra.training.lr_finder import LRRangeFinder
from terraspectra.training.sampler import get_weighted_sampler
from terraspectra.training.tracking import (
    CheckpointRegistry,
    ExperimentTracker,
    generate_results_table,
)


def test_weighted_random_sampler_distribution() -> None:
    """Test that WeightedRandomSampler increases minority class selection."""
    # Highly imbalanced targets: 90 healthy (0), 8 pre-symptomatic (1), 2 diseased (2)
    targets = [0] * 90 + [1] * 8 + [2] * 2
    sampler = get_weighted_sampler(targets, num_classes=3, num_samples=1000)

    sampled_indices = list(sampler)
    sampled_targets = [targets[idx] for idx in sampled_indices]

    # Without weighting, class 2 would be ~2% of samples.
    # With inverse frequency weighting, class 2 should be substantially higher (~20-40%).
    class_2_count = sampled_targets.count(2)
    assert class_2_count > 100  # Should be ~333 on average


def test_model_ema_update_and_restore() -> None:
    """Test ModelEMA shadow parameter tracking, weight application, and restoration."""
    model = nn.Sequential(nn.Linear(8, 4), nn.ReLU(), nn.Linear(4, 2))
    ema = ModelEMA(model, decay=0.9)

    # Initial weights should match
    for name, param in model.named_parameters():
        assert torch.allclose(ema.shadow[name], param.data)

    # Perturb model weights
    with torch.no_grad():
        for param in model.parameters():
            param.data.add_(1.0)

    # Update EMA
    ema.update(model)

    # Apply shadow to model
    ema.apply_shadow(model)
    # Check that model weights are now close to shadow
    for name, param in model.named_parameters():
        assert torch.allclose(param.data, ema.shadow[name])

    # Restore original weights
    ema.restore(model)
    # Check backup was cleared
    assert len(ema.backup) == 0


def test_lr_range_finder() -> None:
    """Test LRRangeFinder sweeping learning rates over batches."""
    x = torch.randn(32, 1, 8, 5, 5)
    y = torch.randint(0, 3, (32,))
    loader = DataLoader(TensorDataset(x, y), batch_size=8)

    model = CNN3DClassifier(CNN3DConfig(depth=8, patch_size=5, base_channels=4, num_classes=3))
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-5)
    criterion = nn.CrossEntropyLoss()

    finder = LRRangeFinder(model, optimizer, criterion)
    results = finder.range_test(loader, start_lr=1e-6, end_lr=1e-1, num_iter=4)

    assert "lrs" in results
    assert "losses" in results
    assert "suggested_lr" in results
    assert len(results["lrs"]) > 0


def test_experiment_tracker_and_checkpoint_registry() -> None:
    """Test ExperimentTracker directories, metadata, CSV metrics, and registry."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        tracker = ExperimentTracker(experiment_name="test_run", base_dir=tmp_path)
        assert tracker.run_dir.exists()

        # Snapshot config
        cfg = {"lr": 0.001, "batch_size": 16}
        snap_file = tracker.snapshot_config(cfg)
        assert snap_file.exists()

        # Metadata
        meta_file = tracker.write_metadata(
            model_name="cnn3d_v1", num_parameters=12345, device="cpu"
        )
        assert meta_file.exists()

        # Metrics logging
        tracker.log_metrics(1, {"train_loss": 0.5, "val_macro_f1": 0.85})
        assert tracker.csv_path.exists()
        tracker.close()

        # Checkpoint registry
        registry = CheckpointRegistry(base_dir=tmp_path)
        dummy_ckpt = tmp_path / "model_epoch1.pt"
        torch.save({"dummy": 1}, dummy_ckpt)

        registry.register(
            checkpoint_path=dummy_ckpt,
            metric_name="val_macro_f1",
            metric_value=0.85,
            epoch=1,
            is_best=True,
        )

        best = registry.get_best_checkpoint("val_macro_f1")
        assert best is not None
        assert best["metric_value"] == 0.85

        best_link = tmp_path / "best_model.pt"
        assert best_link.exists()

        # Results table
        table = generate_results_table(runs_dir=tmp_path)
        assert "Macro-F1" in table


def test_windowed_scene_prediction_and_evaluation() -> None:
    """Test windowed scene prediction, GeoTIFF writing, and evaluation report generation."""
    # Small synthetic scene cube [8, 15, 15]
    cube = np.random.randn(8, 15, 15).astype(np.float32)

    model = CNN3DClassifier(CNN3DConfig(depth=8, patch_size=5, base_channels=4, num_classes=3))
    class_map, risk_map, unc_map = windowed_scene_predict(
        model=model, cube=cube, patch_size=5, batch_size=16, device="cpu"
    )

    assert class_map.shape == (15, 15)
    assert risk_map.shape == (15, 15)
    assert unc_map.shape == (15, 15)
    assert 0 <= class_map.max() <= 2
    assert 0.0 <= risk_map.max() <= 1.0

    # Spectral signatures
    signatures = compute_spectral_signatures(cube, class_map)
    assert "healthy" in signatures
    assert len(signatures["healthy"]) == 8

    with tempfile.TemporaryDirectory() as tmp_dir:
        report = generate_evaluation_report(
            class_map=class_map,
            risk_map=risk_map,
            uncertainty_map=unc_map,
            cube=cube,
            output_dir=tmp_dir,
        )

        assert "summary" in report
        assert "high_risk_acres" in report["summary"]
        assert (Path(tmp_dir) / "evaluation_metrics.json").exists()
