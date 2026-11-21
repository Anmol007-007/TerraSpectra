"""Unit tests for SpectralViT model, configuration, and registry."""

import pytest
import torch

from terraspectra.models.registry import model_registry
from terraspectra.models.vit import SpectralViT, ViTConfig, count_parameters


def test_vit_config_defaults() -> None:
    """Test ViTConfig default hyperparameter values."""
    config = ViTConfig()
    assert config.spectral_dim == 32
    assert config.group_size == 4
    assert config.d_model == 128
    assert config.n_layers == 4
    assert config.n_heads == 4
    assert config.num_classes == 3
    assert config.pooling == "cls"


def test_spectral_vit_forward_and_backward() -> None:
    """Test SpectralViT forward pass and backward loss gradient calculation."""
    b, c, d, h, w = 2, 1, 32, 11, 11
    config = ViTConfig(
        spectral_dim=32,
        group_size=4,
        spatial_patch_size=11,
        d_model=64,
        n_layers=2,
        n_heads=2,
        num_classes=3,
        pooling="cls",
    )
    model = SpectralViT(config=config)
    x = torch.randn(b, c, d, h, w, requires_grad=True)

    logits = model(x)
    assert isinstance(logits, torch.Tensor)
    assert logits.shape == (b, 3)

    loss = logits.sum()
    loss.backward()

    assert x.grad is not None
    assert not torch.isnan(x.grad).any()
    assert x.grad.abs().sum() > 0


def test_spectral_vit_mean_pooling() -> None:
    """Test SpectralViT forward pass with mean pooling option."""
    config = ViTConfig(
        spectral_dim=16,
        group_size=4,
        d_model=32,
        n_layers=1,
        n_heads=2,
        num_classes=3,
        pooling="mean",
    )
    model = SpectralViT(config=config)
    x = torch.randn(2, 1, 16, 11, 11)
    logits = model(x)
    assert logits.shape == (2, 3)


def test_spectral_vit_attention_weights() -> None:
    """Test SpectralViT returning attention weight matrices for explainability."""
    config = ViTConfig(
        spectral_dim=16,
        group_size=4,
        d_model=32,
        n_layers=2,
        n_heads=2,
        num_classes=3,
    )
    model = SpectralViT(config=config)
    x = torch.randn(2, 1, 16, 11, 11)

    logits, attn_weights = model(x, return_attention_weights=True)  # type: ignore[misc]
    assert logits.shape == (2, 3)
    assert len(attn_weights) == 2
    # Seq length is 1 (CLS) + 4 (groups) = 5
    assert attn_weights[0].shape == (2, 2, 5, 5)


def test_spectral_vit_parameter_count_and_init() -> None:
    """Test parameter count calculation and truncated normal initialization."""
    config = ViTConfig(
        spectral_dim=32,
        group_size=4,
        d_model=64,
        n_layers=2,
        n_heads=2,
    )
    model = SpectralViT(config=config)
    params = count_parameters(model)
    assert params > 10000

    # Ensure no NaN weights
    for param in model.parameters():
        assert not torch.isnan(param).any()


def test_spectral_vit_model_registry() -> None:
    """Test that SpectralViT is registered in global model registry."""
    assert "spectral_vit_v1" in model_registry.list_models()
    assert "spectral_vit" in model_registry.list_models()

    instance = model_registry.build("spectral_vit_v1", spectral_dim=16, group_size=4, d_model=32, n_layers=1)
    assert isinstance(instance, SpectralViT)
