"""Unit tests for 3D-CNN building blocks, CNN3D classifier, and model registry."""

from __future__ import annotations

import pytest
import torch

from terraspectra.models.blocks3d import (
    Conv3DBlock,
    GlobalPoolingHead,
    ResidualBlock3D,
    SESpectralAttention,
    SpectralPooling,
    StemBlock3D,
)
from terraspectra.models.cnn3d import (
    CNN3DClassifier,
    CNN3DConfig,
    count_parameters,
    model_summary,
)
from terraspectra.models.registry import ModelRegistry, model_registry


def test_conv3d_block_shape() -> None:
    """Test standard 3D conv block output tensor dimensions."""
    block = Conv3DBlock(in_channels=8, out_channels=16, kernel_size=3, stride=1, padding=1)
    x = torch.randn(2, 8, 16, 11, 11)
    out = block(x)
    assert out.shape == (2, 16, 16, 11, 11)


def test_residual_block_and_gradient_flow() -> None:
    """Test residual 3D block with downsampling and gradient propagation."""
    # Downsample spectral dimension by stride 2
    block = ResidualBlock3D(in_channels=16, out_channels=32, stride=(2, 1, 1), use_se=True)
    x = torch.randn(2, 16, 16, 11, 11, requires_grad=True)
    out = block(x)
    assert out.shape == (2, 32, 8, 11, 11)

    loss = out.sum()
    loss.backward()
    assert x.grad is not None
    assert not torch.isnan(x.grad).any()


def test_se_spectral_attention() -> None:
    """Test Squeeze-and-Excitation spectral attention modulation."""
    se = SESpectralAttention(channels=32, reduction=4)
    x = torch.randn(2, 32, 8, 11, 11)
    out = se(x)
    assert out.shape == x.shape


def test_stem_and_pooling_layers() -> None:
    """Test 3D stem projection and pooling layers."""
    stem = StemBlock3D(in_channels=1, out_channels=16, kernel_size=(3, 3, 3))
    x = torch.randn(2, 1, 32, 11, 11)
    stem_out = stem(x)
    assert stem_out.shape == (2, 16, 32, 11, 11)

    spec_pool = SpectralPooling(pool_factor=2)
    pool_out = spec_pool(stem_out)
    assert pool_out.shape == (2, 16, 16, 11, 11)

    global_pool = GlobalPoolingHead()
    features = global_pool(pool_out)
    assert features.shape == (2, 16)


def test_cnn3d_classifier_forward_pass() -> None:
    """Test complete forward pass of CNN3DClassifier with 5D and 4D inputs."""
    config = CNN3DConfig(
        in_channels=1,
        depth=32,
        patch_size=11,
        base_channels=16,
        num_classes=3,
        dropout=0.1,
    )
    model = CNN3DClassifier(config)

    # 5D input: [B, 1, D, H, W]
    x5d = torch.randn(4, 1, 32, 11, 11)
    out = model(x5d)
    assert "logits" in out and "features" in out
    assert out["logits"].shape == (4, 3)
    assert out["features"].shape == (4, 128)

    # 4D input: [B, D, H, W] (implicitly unsqueezed to 5D)
    x4d = torch.randn(2, 32, 11, 11)
    out4d = model(x4d)
    assert out4d["logits"].shape == (2, 3)


def test_parameter_counts_and_summary() -> None:
    """Test parameter counter utility and summary formatting."""
    model = CNN3DClassifier(CNN3DConfig(base_channels=8))
    counts = count_parameters(model)
    assert counts["trainable"] > 0
    assert counts["trainable"] == counts["total"]

    summary = model_summary(model, input_size=(1, 1, 32, 11, 11))
    assert "CNN3DClassifier" in summary
    assert "Trainable params:" in summary


def test_model_registry() -> None:
    """Test registration and building via ModelRegistry."""
    registry = ModelRegistry()
    registry.register("custom_cnn", CNN3DClassifier)
    assert "custom_cnn" in registry.list_models()

    built = registry.build("custom_cnn", base_channels=8)
    assert isinstance(built, CNN3DClassifier)

    with pytest.raises(ValueError, match="already registered"):
        registry.register("custom_cnn", CNN3DClassifier)

    with pytest.raises(KeyError, match="not found"):
        registry.build("non_existent")

    assert "cnn3d_v1" in model_registry.list_models()
