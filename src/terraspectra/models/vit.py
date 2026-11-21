"""Spectral Vision Transformer (SpectralViT) for hyperspectral crop disease forecasting.

Implements a pure spectral ViT that processes 5D volumetric patches [B, C, D, H, W]
using spectral group tokenisation, pre-norm Transformer encoder layers, and CLS / mean pooling.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Tuple, Union

import torch
import torch.nn as nn
from torch import Tensor

from terraspectra.models.attention import TransformerEncoder
from terraspectra.models.registry import model_registry
from terraspectra.models.tokens import BandGroupingConfig, SpectralGroupTokenizer


def count_parameters(model: nn.Module, trainable_only: bool = True) -> int:
    """Count the total or trainable parameters in a PyTorch module."""
    if trainable_only:
        return sum(p.numel() for p in model.parameters() if p.requires_grad)
    return sum(p.numel() for p in model.parameters())


@dataclass
class ViTConfig:
    """Hyperparameter configuration for SpectralViT architecture.

    Attributes:
        in_channels: Input channels (typically 1 for raw/PCA hyperspectral patch).
        spectral_dim: Number of spectral bands or PCA components (D).
        group_size: Number of adjacent bands grouped per token (g).
        spatial_patch_size: Spatial patch dimension (H = W, default 11).
        d_model: Transformer token embedding dimension.
        n_layers: Number of Transformer encoder blocks.
        n_heads: Number of multi-head attention heads.
        mlp_ratio: Ratio of MLP hidden dimension to d_model.
        dropout: Token and projection dropout probability.
        attention_dropout: Attention matrix dropout probability.
        stochastic_depth: Maximum drop-path probability across layers.
        pooling: Sequence pooling method ('cls' or 'mean').
        pos_embedding_type: Positional encoding type ('learned', 'sinusoidal', 'wavelength').
        wavelengths: Physical wavelengths (nm) when pos_embedding_type='wavelength'.
        num_classes: Number of disease target classes (0: healthy, 1: pre-symptomatic, 2: diseased).
    """

    in_channels: int = 1
    spectral_dim: int = 32
    group_size: int = 4
    spatial_patch_size: int = 11
    d_model: int = 128
    n_layers: int = 4
    n_heads: int = 4
    mlp_ratio: float = 4.0
    dropout: float = 0.1
    attention_dropout: float = 0.1
    stochastic_depth: float = 0.1
    pooling: Literal["cls", "mean"] = "cls"
    pos_embedding_type: Literal["learned", "sinusoidal", "wavelength"] = "learned"
    wavelengths: list[float] | None = None
    num_classes: int = 3
    extra: dict[str, Any] = field(default_factory=dict)


class SpectralViT(nn.Module):
    """Spectral Vision Transformer for hyperspectral crop disease detection.

    Processes 5D hyperspectral volumes [B, C, D, H, W] through:
    1. SpectralGroupTokenizer: patch embedding, CLS token, position encoding.
    2. TransformerEncoder: pre-norm self-attention blocks with stochastic depth.
    3. Pooling: CLS token pooling or mean sequence pooling.
    4. Head: linear classification head mapping d_model -> num_classes.
    """

    def __init__(self, config: ViTConfig | None = None, **kwargs: Any) -> None:
        super().__init__()
        if config is None:
            config = ViTConfig(**kwargs)
        self.config = config

        # 1. Tokenizer
        tokenizer_cfg = BandGroupingConfig(
            spectral_dim=config.spectral_dim,
            group_size=config.group_size,
            in_channels=config.in_channels,
            d_model=config.d_model,
            spatial_patch_size=config.spatial_patch_size,
            pos_embedding_type=config.pos_embedding_type,
            wavelengths=config.wavelengths,
            dropout=config.dropout,
        )
        self.tokenizer = SpectralGroupTokenizer(config=tokenizer_cfg)

        # 2. Transformer Encoder Stack
        self.encoder = TransformerEncoder(
            d_model=config.d_model,
            n_layers=config.n_layers,
            n_heads=config.n_heads,
            mlp_ratio=config.mlp_ratio,
            dropout=config.dropout,
            attn_dropout=config.attention_dropout,
            stochastic_depth=config.stochastic_depth,
        )

        # 3. Pooling and Classification Head
        self.pooling = config.pooling
        self.norm = nn.LayerNorm(config.d_model)
        self.head = nn.Linear(config.d_model, config.num_classes)

        # 4. Weight initialisation
        self.apply(self._init_weights)

    def _init_weights(self, m: nn.Module) -> None:
        """Initialise weights with truncated normal distribution (ViT standard)."""
        if isinstance(m, nn.Linear):
            nn.init.trunc_normal_(m.weight, std=0.02)
            if m.bias is not None:
                nn.init.zeros_(m.bias)
        elif isinstance(m, nn.LayerNorm):
            nn.init.ones_(m.weight)
            nn.init.zeros_(m.bias)

    def extract_features(
        self, x: Tensor, return_attention_weights: bool = False
    ) -> Union[Tensor, Tuple[Tensor, list[Tensor]]]:
        """Extract pooled d_model representation vectors from 5D input tensor.

        Args:
            x: Input tensor [B, C, D, H, W].
            return_attention_weights: If True, returns (pooled_features, attn_weights_list).

        Returns:
            Pooled feature tensor [B, d_model] or (features, attn_weights).
        """
        # Tokenise: [B, 1 + T, d_model]
        tokens = self.tokenizer(x)

        if return_attention_weights:
            tokens_res = self.encoder(tokens, return_attention_weights=True)
            encoded_tokens, attn_weights = tokens_res  # type: ignore[misc]
        else:
            encoded_tokens = self.encoder(tokens, return_attention_weights=False)
            assert isinstance(encoded_tokens, Tensor)
            attn_weights = []

        # Pooling
        if self.pooling == "cls":
            pooled = encoded_tokens[:, 0]  # CLS token at position 0
        elif self.pooling == "mean":
            # Average over all spectral group tokens (excluding CLS token)
            pooled = encoded_tokens[:, 1:].mean(dim=1)
        else:
            raise ValueError(f"Unsupported pooling mode: {self.pooling}")

        features = self.norm(pooled)
        if return_attention_weights:
            return features, attn_weights
        return features

    def forward(
        self, x: Tensor, return_attention_weights: bool = False
    ) -> Union[Tensor, Tuple[Tensor, list[Tensor]]]:
        """Forward pass predicting disease state logits.

        Args:
            x: Input tensor [B, C, D, H, W].
            return_attention_weights: If True, returns (logits, attention_weights).

        Returns:
            Class logits [B, num_classes] or (logits, list_of_attn_weights).
        """
        if return_attention_weights:
            features, weights = self.extract_features(x, return_attention_weights=True)  # type: ignore[misc]
            logits = self.head(features)
            return logits, weights

        features = self.extract_features(x, return_attention_weights=False)
        assert isinstance(features, Tensor)
        return self.head(features)


# Register in global model registry
model_registry.register("spectral_vit_v1", SpectralViT)
model_registry.register("spectral_vit", SpectralViT)
