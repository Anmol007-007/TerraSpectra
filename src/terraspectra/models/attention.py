"""Multi-head self-attention and Transformer encoder blocks for SpectralViT.

Implements pre-norm Transformer architecture with:
- MultiHeadSelfAttention using PyTorch scaled_dot_product_attention (with weight extraction mode)
- Stochastic depth (DropPath)
- Pre-LayerNorm and GELU activations
- TransformerEncoderBlock and TransformerEncoder stack
- Attention rollout and explainability hooks
"""

from __future__ import annotations

import math
from typing import Tuple, Union

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor


class DropPath(nn.Module):
    """Drop paths (Stochastic Depth) per sample when applied in residual blocks.

    During training, randomly sets a sample's entire residual branch to zero with
    probability `drop_prob`, scaling surviving samples by 1 / (1 - drop_prob).
    """

    def __init__(self, drop_prob: float = 0.0) -> None:
        super().__init__()
        self.drop_prob = float(drop_prob)

    def forward(self, x: Tensor) -> Tensor:
        if self.drop_prob == 0.0 or not self.training:
            return x
        keep_prob = 1.0 - self.drop_prob
        shape = (x.shape[0],) + (1,) * (x.ndim - 1)
        random_tensor = keep_prob + torch.rand(shape, dtype=x.dtype, device=x.device)
        random_tensor.floor_()  # binarise to 0 or 1
        return x.div(keep_prob) * random_tensor


class MultiHeadSelfAttention(nn.Module):
    """Multi-Head Self-Attention with scaled dot-product and optional attention weights extraction.

    Args:
        d_model: Feature dimension of input and output tokens.
        n_heads: Number of parallel attention heads.
        attn_dropout: Dropout probability applied to attention weights.
        proj_dropout: Dropout probability applied after final linear projection.
        qkv_bias: Whether to include bias terms in query, key, value projections.
    """

    def __init__(
        self,
        d_model: int = 128,
        n_heads: int = 4,
        attn_dropout: float = 0.1,
        proj_dropout: float = 0.1,
        qkv_bias: bool = True,
    ) -> None:
        super().__init__()
        if d_model % n_heads != 0:
            raise ValueError(f"d_model ({d_model}) must be divisible by n_heads ({n_heads})")

        self.d_model = d_model
        self.n_heads = n_heads
        self.head_dim = d_model // n_heads
        self.scale = 1.0 / math.sqrt(self.head_dim)
        self.attn_dropout_p = attn_dropout

        self.qkv = nn.Linear(d_model, d_model * 3, bias=qkv_bias)
        self.attn_drop = nn.Dropout(attn_dropout)
        self.proj = nn.Linear(d_model, d_model)
        self.proj_drop = nn.Dropout(proj_dropout)

    def forward(
        self, x: Tensor, return_attention_weights: bool = False
    ) -> Union[Tensor, Tuple[Tensor, Tensor]]:
        """Forward pass for multi-head self-attention.

        Args:
            x: Input token tensor [B, S, d_model].
            return_attention_weights: If True, returns (output, attention_weights) where
                attention_weights is [B, n_heads, S, S].

        Returns:
            Output tensor [B, S, d_model], or (output, weights) tuple.
        """
        b, s, c = x.shape
        # Compute Q, K, V: [B, S, 3, n_heads, head_dim] -> permute to 3 x [B, n_heads, S, head_dim]
        qkv = self.qkv(x).reshape(b, s, 3, self.n_heads, self.head_dim).permute(2, 0, 3, 1, 4)
        q, k, v = qkv[0], qkv[1], qkv[2]

        if return_attention_weights:
            # Explicit attention computation to capture weight matrix
            attn_scores = torch.matmul(q, k.transpose(-2, -1)) * self.scale  # [B, n_heads, S, S]
            attn_weights = F.softmax(attn_scores, dim=-1)
            attn_weights_dropped = self.attn_drop(attn_weights)
            out = torch.matmul(attn_weights_dropped, v)  # [B, n_heads, S, head_dim]
            out = out.transpose(1, 2).reshape(b, s, c)  # [B, S, d_model]
            out = self.proj_drop(self.proj(out))
            return out, attn_weights

        # Optimized Flash / Memory-efficient PyTorch attention
        dropout_p = self.attn_dropout_p if self.training else 0.0
        out = F.scaled_dot_product_attention(
            q, k, v, dropout_p=dropout_p, scale=self.scale
        )
        out = out.transpose(1, 2).reshape(b, s, c)
        out = self.proj_drop(self.proj(out))
        return out


class MLPBlock(nn.Module):
    """Feed-Forward Network (MLP) block for Transformer encoder.

    Follows standard ViT MLP: Linear -> GELU -> Dropout -> Linear -> Dropout.
    """

    def __init__(
        self,
        d_model: int = 128,
        mlp_ratio: float = 4.0,
        dropout: float = 0.1,
        act_layer: type[nn.Module] = nn.GELU,
    ) -> None:
        super().__init__()
        hidden_dim = int(d_model * mlp_ratio)
        self.fc1 = nn.Linear(d_model, hidden_dim)
        self.act = act_layer()
        self.drop1 = nn.Dropout(dropout)
        self.fc2 = nn.Linear(hidden_dim, d_model)
        self.drop2 = nn.Dropout(dropout)

    def forward(self, x: Tensor) -> Tensor:
        return self.drop2(self.fc2(self.drop1(self.act(self.fc1(x)))))


class TransformerEncoderBlock(nn.Module):
    """Pre-Norm Transformer Encoder Block with Stochastic Depth.

    Architecture:
    x = x + DropPath(Attention(LayerNorm(x)))
    x = x + DropPath(MLP(LayerNorm(x)))
    """

    def __init__(
        self,
        d_model: int = 128,
        n_heads: int = 4,
        mlp_ratio: float = 4.0,
        dropout: float = 0.1,
        attn_dropout: float = 0.1,
        drop_path: float = 0.0,
    ) -> None:
        super().__init__()
        self.norm1 = nn.LayerNorm(d_model)
        self.attn = MultiHeadSelfAttention(
            d_model=d_model,
            n_heads=n_heads,
            attn_dropout=attn_dropout,
            proj_dropout=dropout,
        )
        self.drop_path1 = DropPath(drop_path) if drop_path > 0.0 else nn.Identity()

        self.norm2 = nn.LayerNorm(d_model)
        self.mlp = MLPBlock(
            d_model=d_model,
            mlp_ratio=mlp_ratio,
            dropout=dropout,
        )
        self.drop_path2 = DropPath(drop_path) if drop_path > 0.0 else nn.Identity()

    def forward(
        self, x: Tensor, return_attention_weights: bool = False
    ) -> Union[Tensor, Tuple[Tensor, Tensor]]:
        """Forward pass through encoder block.

        Returns:
            Output tensor [B, S, d_model] or (output, weights).
        """
        x_norm = self.norm1(x)
        if return_attention_weights:
            attn_res = self.attn(x_norm, return_attention_weights=True)
            attn_out, weights = attn_res  # type: ignore[misc]
            x = x + self.drop_path1(attn_out)
            x = x + self.drop_path2(self.mlp(self.norm2(x)))
            return x, weights

        attn_out = self.attn(x_norm, return_attention_weights=False)
        assert isinstance(attn_out, Tensor)
        x = x + self.drop_path1(attn_out)
        x = x + self.drop_path2(self.mlp(self.norm2(x)))
        return x


class TransformerEncoder(nn.Module):
    """Stack of TransformerEncoderBlocks with stochastic depth linear decay and final LayerNorm."""

    def __init__(
        self,
        d_model: int = 128,
        n_layers: int = 4,
        n_heads: int = 4,
        mlp_ratio: float = 4.0,
        dropout: float = 0.1,
        attn_dropout: float = 0.1,
        stochastic_depth: float = 0.1,
    ) -> None:
        super().__init__()
        self.d_model = d_model
        self.n_layers = n_layers

        # Linear stochastic depth decay rule across encoder depth
        dpr = [
            float(x) for x in torch.linspace(0, stochastic_depth, n_layers)
        ]

        self.blocks = nn.ModuleList(
            [
                TransformerEncoderBlock(
                    d_model=d_model,
                    n_heads=n_heads,
                    mlp_ratio=mlp_ratio,
                    dropout=dropout,
                    attn_dropout=attn_dropout,
                    drop_path=dpr[i],
                )
                for i in range(n_layers)
            ]
        )
        self.norm = nn.LayerNorm(d_model)

    def forward(
        self, x: Tensor, return_attention_weights: bool = False
    ) -> Union[Tensor, Tuple[Tensor, list[Tensor]]]:
        """Forward pass through all encoder blocks.

        Args:
            x: Sequence tensor [B, S, d_model].
            return_attention_weights: If True, also returns list of attention weight tensors.

        Returns:
            Normalized output tensor [B, S, d_model], or (output, list_of_attn_weights).
        """
        all_weights: list[Tensor] = []
        for block in self.blocks:
            assert isinstance(block, TransformerEncoderBlock)
            if return_attention_weights:
                x_res = block(x, return_attention_weights=True)
                x, weights = x_res  # type: ignore[misc]
                all_weights.append(weights)
            else:
                x_out = block(x, return_attention_weights=False)
                assert isinstance(x_out, Tensor)
                x = x_out

        x_out = self.norm(x)
        if return_attention_weights:
            return x_out, all_weights
        return x_out
