"""Unit tests for CNN-to-Token Feature Adapter."""

import pytest
import torch

from terraspectra.models.tokens import CNNToTokenAdapter, InvalidDimensionError


def test_cnn_to_token_adapter_shapes() -> None:
    """Test standard shape conversion from 5D CNN output to sequence tokens."""
    b, c, d, h, w = 4, 64, 16, 5, 5
    d_model = 128
    group_size = 4
    x = torch.randn(b, c, d, h, w)

    adapter = CNNToTokenAdapter(
        in_channels=c,
        spectral_dim=d,
        group_size=group_size,
        d_model=d_model,
        spatial_pooling="avg",
    )

    tokens = adapter(x)
    # Expected: num_tokens = 16 // 4 = 4 tokens of dimension d_model=128
    assert tokens.shape == (b, 4, d_model)


def test_cnn_to_token_adapter_center_pooling() -> None:
    """Test CNNToTokenAdapter with centre pixel spatial pooling."""
    b, c, d, h, w = 2, 32, 8, 7, 7
    d_model = 64
    x = torch.randn(b, c, d, h, w)

    adapter = CNNToTokenAdapter(
        in_channels=c,
        spectral_dim=d,
        group_size=2,
        d_model=d_model,
        spatial_pooling="center",
    )

    tokens = adapter(x)
    assert tokens.shape == (b, 4, d_model)


def test_cnn_to_token_adapter_dimension_validation_errors() -> None:
    """Test that InvalidDimensionError is raised on incompatible tensor shapes."""
    # Invalid spectral_dim indivisible by group_size
    with pytest.raises(InvalidDimensionError):
        CNNToTokenAdapter(in_channels=64, spectral_dim=15, group_size=4)

    adapter = CNNToTokenAdapter(in_channels=64, spectral_dim=16, group_size=4, d_model=128)

    # Wrong tensor rank (4D instead of 5D)
    with pytest.raises(InvalidDimensionError):
        adapter(torch.randn(2, 64, 16, 5))

    # Channel mismatch
    with pytest.raises(InvalidDimensionError):
        adapter(torch.randn(2, 32, 16, 5, 5))

    # Spectral dimension mismatch
    with pytest.raises(InvalidDimensionError):
        adapter(torch.randn(2, 64, 32, 5, 5))
