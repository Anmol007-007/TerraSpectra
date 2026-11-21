"""Unit tests for Multi-Head Attention and Transformer Encoder."""

import pytest
import torch
import torch.nn as nn

from terraspectra.models.attention import (
    DropPath,
    MLPBlock,
    MultiHeadSelfAttention,
    TransformerEncoder,
    TransformerEncoderBlock,
)


def test_multi_head_attention_output_shape() -> None:
    """Test output shapes of MultiHeadSelfAttention under standard execution."""
    b, s, d_model = 2, 9, 128
    x = torch.randn(b, s, d_model)
    attn = MultiHeadSelfAttention(d_model=d_model, n_heads=4, attn_dropout=0.0)

    out = attn(x, return_attention_weights=False)
    assert isinstance(out, torch.Tensor)
    assert out.shape == (b, s, d_model)


def test_attention_weights_sum_to_one() -> None:
    """Test that explicit attention weights sum to 1.0 along the key dimension."""
    b, s, d_model, n_heads = 2, 9, 128, 4
    x = torch.randn(b, s, d_model)
    attn = MultiHeadSelfAttention(d_model=d_model, n_heads=n_heads, attn_dropout=0.0)
    attn.eval()

    out, weights = attn(x, return_attention_weights=True)  # type: ignore[misc]
    assert out.shape == (b, s, d_model)
    assert weights.shape == (b, n_heads, s, s)

    # Weights sum to 1 along the last dimension (keys)
    sums = weights.sum(dim=-1)
    ones = torch.ones_like(sums)
    assert torch.allclose(sums, ones, atol=1e-5)


def test_drop_path() -> None:
    """Test DropPath (stochastic depth) behavior during train and eval modes."""
    drop = DropPath(drop_prob=0.5)
    x = torch.ones(10, 4, 32)

    # In eval mode, DropPath is identity
    drop.eval()
    assert torch.allclose(drop(x), x)

    # In train mode, some elements should be 0 across samples
    drop.train()
    torch.manual_seed(42)
    out_train = drop(x)
    assert out_train.shape == x.shape


def test_mlp_block() -> None:
    """Test MLPBlock forward pass and shape preservation."""
    b, s, d_model = 3, 9, 64
    mlp = MLPBlock(d_model=d_model, mlp_ratio=4.0)
    x = torch.randn(b, s, d_model)
    out = mlp(x)
    assert out.shape == (b, s, d_model)


def test_transformer_encoder_block() -> None:
    """Test TransformerEncoderBlock forward with and without returning weights."""
    b, s, d_model = 2, 9, 64
    block = TransformerEncoderBlock(d_model=d_model, n_heads=4, drop_path=0.1)
    x = torch.randn(b, s, d_model)

    # Normal pass
    out = block(x, return_attention_weights=False)
    assert isinstance(out, torch.Tensor)
    assert out.shape == (b, s, d_model)

    # Attention weights pass
    out2, w = block(x, return_attention_weights=True)  # type: ignore[misc]
    assert out2.shape == (b, s, d_model)
    assert w.shape == (b, 4, s, s)


def test_encoder_gradient_flow() -> None:
    """Test that gradients flow smoothly through all encoder layers without vanishing/exploding."""
    b, s, d_model = 2, 9, 64
    encoder = TransformerEncoder(
        d_model=d_model,
        n_layers=3,
        n_heads=4,
        mlp_ratio=2.0,
        dropout=0.0,
        attn_dropout=0.0,
        stochastic_depth=0.0,
    )
    x = torch.randn(b, s, d_model, requires_grad=True)

    out = encoder(x, return_attention_weights=False)
    assert isinstance(out, torch.Tensor)
    loss = out.sum()
    loss.backward()

    # Verify input gradient exists
    assert x.grad is not None
    assert not torch.isnan(x.grad).any()
    assert x.grad.abs().sum() > 0

    # Verify all encoder parameter gradients exist
    for name, param in encoder.named_parameters():
        assert param.grad is not None, f"Gradient is None for {name}"
        assert not torch.isnan(param.grad).any(), f"NaN gradient in {name}"
        assert param.grad.abs().sum() > 0, f"Zero gradient in {name}"
