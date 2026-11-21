"""Unit tests for spectral tokenisation, patch embeddings, and positional encodings."""

import pytest
import torch

from terraspectra.models.tokens import (
    BandGroupingConfig,
    InvalidDimensionError,
    LearnedPositionalEmbedding,
    SinusoidalPositionalEmbedding,
    SpatialSpectralPatchEmbedding,
    SpectralGroupTokenizer,
    WavelengthAwarePositionalEncoding,
)


def test_band_grouping_config_valid() -> None:
    """Test valid BandGroupingConfig creation and properties."""
    cfg = BandGroupingConfig(spectral_dim=32, group_size=4, d_model=128)
    assert cfg.num_tokens == 8
    assert cfg.spectral_dim == 32
    assert cfg.group_size == 4


def test_band_grouping_config_invalid() -> None:
    """Test invalid BandGroupingConfig raises InvalidDimensionError."""
    with pytest.raises(InvalidDimensionError):
        BandGroupingConfig(spectral_dim=30, group_size=4)

    with pytest.raises(InvalidDimensionError):
        BandGroupingConfig(spectral_dim=0, group_size=4)

    with pytest.raises(InvalidDimensionError):
        BandGroupingConfig(spectral_dim=32, group_size=-1)


def test_spatial_spectral_patch_embedding_shapes() -> None:
    """Test SpatialSpectralPatchEmbedding output shapes with both pooling modes."""
    b, c, d, h, w = 2, 1, 32, 11, 11
    d_model = 64
    x = torch.randn(b, c, d, h, w)

    # Mode 1: avg_pool
    embed_avg = SpatialSpectralPatchEmbedding(
        in_channels=1, spectral_dim=32, group_size=4, d_model=d_model, spatial_mode="avg_pool"
    )
    tokens_avg = embed_avg(x)
    assert tokens_avg.shape == (b, 8, d_model)

    # Mode 2: flatten_linear
    embed_flat = SpatialSpectralPatchEmbedding(
        in_channels=1,
        spectral_dim=32,
        group_size=4,
        d_model=d_model,
        spatial_mode="flatten_linear",
        spatial_patch_size=11,
    )
    tokens_flat = embed_flat(x)
    assert tokens_flat.shape == (b, 8, d_model)


def test_spatial_spectral_patch_embedding_invalid_dims() -> None:
    """Test InvalidDimensionError when passing bad tensor shapes."""
    embed = SpatialSpectralPatchEmbedding(in_channels=1, spectral_dim=32, group_size=4)
    # Wrong rank (4D instead of 5D)
    with pytest.raises(InvalidDimensionError):
        embed(torch.randn(2, 1, 32, 11))

    # Channel mismatch
    with pytest.raises(InvalidDimensionError):
        embed(torch.randn(2, 3, 32, 11, 11))

    # Spectral dim mismatch
    with pytest.raises(InvalidDimensionError):
        embed(torch.randn(2, 1, 16, 11, 11))


def test_positional_embeddings() -> None:
    """Test Learned, Sinusoidal, and WavelengthAware positional encodings."""
    b, seq_len, d_model = 4, 9, 64
    tokens = torch.zeros(b, seq_len, d_model)

    # 1. Learned
    learned = LearnedPositionalEmbedding(seq_len=seq_len, d_model=d_model)
    out_learned = learned(tokens)
    assert out_learned.shape == (b, seq_len, d_model)
    assert not torch.allclose(out_learned, tokens)

    # 2. Sinusoidal
    sinusoidal = SinusoidalPositionalEmbedding(seq_len=seq_len, d_model=d_model)
    out_sin = sinusoidal(tokens)
    assert out_sin.shape == (b, seq_len, d_model)
    assert not torch.allclose(out_sin, tokens)

    # 3. Wavelength-aware (8 spectral bands -> 2 groups of size 4 + 1 CLS token = 3 tokens)
    wavelengths = [450.0, 500.0, 550.0, 600.0, 650.0, 700.0, 750.0, 800.0]
    wl_tokens = torch.zeros(b, 3, d_model)
    wl_pe = WavelengthAwarePositionalEncoding(
        wavelengths=wavelengths, d_model=d_model, group_size=4
    )
    out_wl = wl_pe(wl_tokens)
    assert out_wl.shape == (b, 3, d_model)
    assert not torch.allclose(out_wl, wl_tokens)


def test_spectral_group_tokenizer_full_pipeline() -> None:
    """Test SpectralGroupTokenizer prepends CLS token and applies dropout."""
    cfg = BandGroupingConfig(
        spectral_dim=32,
        group_size=4,
        in_channels=1,
        d_model=128,
        spatial_patch_size=11,
        pos_embedding_type="learned",
        dropout=0.1,
    )
    tokenizer = SpectralGroupTokenizer(config=cfg)

    x = torch.randn(3, 1, 32, 11, 11)
    tokens = tokenizer(x)

    # Total tokens = 1 (CLS) + 8 (spectral groups) = 9
    assert tokens.shape == (3, 9, 128)

    # Check eval mode disables dropout
    tokenizer.eval()
    out1 = tokenizer(x)
    out2 = tokenizer(x)
    assert torch.allclose(out1, out2)
