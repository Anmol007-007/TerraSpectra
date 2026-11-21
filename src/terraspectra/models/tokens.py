"""Spectral tokenisation, patch embeddings, and positional encodings for SpectralViT.

Provides modular tokenisation for hyperspectral data:
- BandGroupingConfig: configuration for band grouping and token embedding.
- SpectralGroupTokenizer: groups spectral bands/PCs into tokens, projects to d_model,
  prepends learnable CLS token, adds positional encodings, and applies token dropout.
- LearnedPositionalEmbedding: learned 1D position embeddings.
- SinusoidalPositionalEmbedding: deterministic sinusoidal position encodings.
- WavelengthAwarePositionalEncoding: continuous sinusoidal encodings driven by physical wavelengths (nm).
- CNNToTokenAdapter: adapts 5D CNN feature volumes [B, C, D, H, W] to sequence tokens [B, T, d_model].
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Literal, Sequence

import torch
import torch.nn as nn
from torch import Tensor


class InvalidDimensionError(ValueError):
    """Raised when tensor dimensions are incompatible with model or tokeniser configuration."""


@dataclass
class BandGroupingConfig:
    """Hyperparameters for spectral band grouping and token projection.

    Attributes:
        spectral_dim: Number of spectral bands or PCA components (depth D).
        group_size: Number of adjacent bands grouped into a single token (g).
        in_channels: Input channels (typically 1 for raw/PCA hyperspectral patch).
        d_model: Target transformer token embedding dimension.
        spatial_patch_size: Spatial patch dimension (H = W).
        pos_embedding_type: Type of positional encoding ('learned', 'sinusoidal', 'wavelength').
        wavelengths: Optional physical wavelengths (in nm) for each spectral band.
        dropout: Token dropout probability.
    """

    spectral_dim: int = 32
    group_size: int = 4
    in_channels: int = 1
    d_model: int = 128
    spatial_patch_size: int = 11
    pos_embedding_type: Literal["learned", "sinusoidal", "wavelength"] = "learned"
    wavelengths: list[float] | None = None
    dropout: float = 0.1
    extra: dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.spectral_dim <= 0:
            raise InvalidDimensionError(f"spectral_dim must be positive, got {self.spectral_dim}")
        if self.group_size <= 0:
            raise InvalidDimensionError(f"group_size must be positive, got {self.group_size}")
        if self.spectral_dim % self.group_size != 0:
            raise InvalidDimensionError(
                f"spectral_dim ({self.spectral_dim}) must be divisible by group_size ({self.group_size})"
            )
        if self.d_model <= 0:
            raise InvalidDimensionError(f"d_model must be positive, got {self.d_model}")
        if self.pos_embedding_type == "wavelength":
            if self.wavelengths is None or len(self.wavelengths) != self.spectral_dim:
                raise ValueError(
                    f"pos_embedding_type='wavelength' requires wavelengths list of length {self.spectral_dim}"
                )

    @property
    def num_tokens(self) -> int:
        """Number of spectral group tokens (excluding CLS token)."""
        return self.spectral_dim // self.group_size


class LearnedPositionalEmbedding(nn.Module):
    """Learned 1D positional embedding for sequence tokens including CLS token."""

    def __init__(self, seq_len: int, d_model: int) -> None:
        super().__init__()
        self.seq_len = seq_len
        self.d_model = d_model
        self.pos_embed = nn.Parameter(torch.zeros(1, seq_len, d_model))
        nn.init.trunc_normal_(self.pos_embed, std=0.02)

    def forward(self, x: Tensor) -> Tensor:
        """Add learned positional embedding to input tokens [B, seq_len, d_model]."""
        if x.size(1) > self.seq_len:
            raise InvalidDimensionError(
                f"Sequence length {x.size(1)} exceeds embedding length {self.seq_len}"
            )
        return x + self.pos_embed[:, : x.size(1), :]


class SinusoidalPositionalEmbedding(nn.Module):
    """Deterministic 1D sinusoidal positional encoding (Vaswani et al.)."""

    def __init__(self, seq_len: int, d_model: int, base: float = 10000.0) -> None:
        super().__init__()
        self.seq_len = seq_len
        self.d_model = d_model

        pe = torch.zeros(seq_len, d_model)
        position = torch.arange(0, seq_len, dtype=torch.float32).unsqueeze(1)
        div_term = torch.exp(
            torch.arange(0, d_model, 2, dtype=torch.float32) * (-math.log(base) / d_model)
        )

        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term[: d_model // 2])
        pe = pe.unsqueeze(0)  # [1, seq_len, d_model]
        self.register_buffer("pe", pe, persistent=False)

    def forward(self, x: Tensor) -> Tensor:
        """Add sinusoidal positional encoding to tokens [B, seq_len, d_model]."""
        pe_buf = getattr(self, "pe")
        return x + pe_buf[:, : x.size(1), :]


class WavelengthAwarePositionalEncoding(nn.Module):
    """Continuous sinusoidal positional encoding based on physical nanometre wavelengths.

    Computes group-average central wavelengths and uses continuous harmonic functions
    so that spectral proximity in physical wavelength space (e.g. red-edge shift ~705 nm)
    is directly encoded into token representations.
    """

    def __init__(
        self,
        wavelengths: Sequence[float],
        d_model: int,
        group_size: int = 4,
        base: float = 10000.0,
    ) -> None:
        super().__init__()
        self.d_model = d_model
        self.group_size = group_size
        num_bands = len(wavelengths)
        if num_bands % group_size != 0:
            raise InvalidDimensionError(
                f"Wavelengths length ({num_bands}) must be divisible by group_size ({group_size})"
            )

        num_tokens = num_bands // group_size
        group_centers: list[float] = []
        for i in range(num_tokens):
            chunk = wavelengths[i * group_size : (i + 1) * group_size]
            group_centers.append(sum(chunk) / len(chunk))

        # Wavelength values scaled to normalized range for stability (~400-2500nm -> ~4.0-25.0)
        centers_t = torch.tensor(group_centers, dtype=torch.float32) / 100.0  # [num_tokens]

        # Positional encodings for tokens: [num_tokens, d_model]
        token_pe = torch.zeros(num_tokens, d_model)
        div_term = torch.exp(
            torch.arange(0, d_model, 2, dtype=torch.float32) * (-math.log(base) / d_model)
        )
        token_pe[:, 0::2] = torch.sin(centers_t.unsqueeze(1) * div_term)
        token_pe[:, 1::2] = torch.cos(centers_t.unsqueeze(1) * div_term[: d_model // 2])

        # Learnable embedding for the CLS token
        self.cls_pos_embed = nn.Parameter(torch.zeros(1, 1, d_model))
        nn.init.trunc_normal_(self.cls_pos_embed, std=0.02)

        pe = token_pe.unsqueeze(0)  # [1, num_tokens, d_model]
        self.register_buffer("pe", pe, persistent=False)

    def forward(self, x: Tensor) -> Tensor:
        """Add wavelength-aware encoding to tokens [B, seq_len, d_model].

        Assumes x[:, 0, :] is CLS token and x[:, 1:, :] are spectral group tokens.
        """
        pe_buf = getattr(self, "pe")
        cls_pe = self.cls_pos_embed  # [1, 1, d_model]
        full_pe = torch.cat([cls_pe, pe_buf], dim=1)  # [1, 1 + num_tokens, d_model]

        if x.size(1) > full_pe.size(1):
            raise InvalidDimensionError(
                f"Sequence length {x.size(1)} exceeds wavelength embedding length {full_pe.size(1)}"
            )
        return x + full_pe[:, : x.size(1), :]


class SpatialSpectralPatchEmbedding(nn.Module):
    """Extracts spatial-spectral patch tokens from 5D hyperspectral tensors [B, C, D, H, W].

    Groups D spectral bands into D // group_size slices. Spatially pools over H x W
    (or projects) and linearly projects each spectral group into d_model dimensions.
    """

    def __init__(
        self,
        in_channels: int = 1,
        spectral_dim: int = 32,
        group_size: int = 4,
        d_model: int = 128,
        spatial_mode: Literal["avg_pool", "flatten_linear"] = "avg_pool",
        spatial_patch_size: int = 11,
    ) -> None:
        super().__init__()
        self.in_channels = in_channels
        self.spectral_dim = spectral_dim
        self.group_size = group_size
        self.d_model = d_model
        self.spatial_mode = spatial_mode

        if spectral_dim % group_size != 0:
            raise InvalidDimensionError(
                f"spectral_dim ({spectral_dim}) must be divisible by group_size ({group_size})"
            )
        self.num_tokens = spectral_dim // group_size

        if spatial_mode == "avg_pool":
            self.spatial_pool = nn.AdaptiveAvgPool2d((1, 1))
            self.proj = nn.Linear(in_channels * group_size, d_model)
        else:
            in_features = in_channels * group_size * spatial_patch_size * spatial_patch_size
            self.proj = nn.Linear(in_features, d_model)

    def forward(self, x: Tensor) -> Tensor:
        """Projects input [B, C, D, H, W] to tokens [B, T, d_model]."""
        if x.dim() != 5:
            raise InvalidDimensionError(f"Expected 5D tensor [B, C, D, H, W], got shape {list(x.shape)}")
        b, c, d, h, w = x.shape
        if c != self.in_channels:
            raise InvalidDimensionError(f"Expected in_channels={self.in_channels}, got {c}")
        if d != self.spectral_dim:
            raise InvalidDimensionError(f"Expected spectral_dim={self.spectral_dim}, got {d}")

        t = self.num_tokens
        g = self.group_size

        if self.spatial_mode == "avg_pool":
            # [B, C, T, g, H, W] -> permute to [B, T, C*g, H, W]
            x_grouped = x.view(b, c, t, g, h, w).permute(0, 2, 1, 3, 4, 5)
            x_grouped = x_grouped.reshape(b * t, c * g, h, w)
            x_pooled = self.spatial_pool(x_grouped).squeeze(-1).squeeze(-1)  # [B*T, C*g]
            tokens = self.proj(x_pooled).view(b, t, self.d_model)
        else:
            x_grouped = x.view(b, c, t, g, h, w).permute(0, 2, 1, 3, 4, 5)
            x_flat = x_grouped.reshape(b, t, c * g * h * w)
            tokens = self.proj(x_flat)

        return tokens


class SpectralGroupTokenizer(nn.Module):
    """Complete spectral tokeniser module for SpectralViT and HybridCNNViT.

    Workflow:
    1. Extracts spatial-spectral patch embeddings from [B, C, D, H, W] -> [B, T, d_model].
    2. Prepends a learnable [CLS] token -> [B, 1 + T, d_model].
    3. Adds positional encoding (learned, sinusoidal, or wavelength-aware).
    4. Applies token dropout.
    """

    def __init__(self, config: BandGroupingConfig | None = None, **kwargs: object) -> None:
        super().__init__()
        if config is None:
            config = BandGroupingConfig(**kwargs)  # type: ignore[arg-type]
        self.config = config

        self.patch_embed = SpatialSpectralPatchEmbedding(
            in_channels=config.in_channels,
            spectral_dim=config.spectral_dim,
            group_size=config.group_size,
            d_model=config.d_model,
            spatial_mode="avg_pool",
            spatial_patch_size=config.spatial_patch_size,
        )

        # Learnable CLS token
        self.cls_token = nn.Parameter(torch.zeros(1, 1, config.d_model))
        nn.init.trunc_normal_(self.cls_token, std=0.02)

        # Positional encoding
        total_tokens = 1 + self.config.num_tokens
        if config.pos_embedding_type == "learned":
            self.pos_embed: nn.Module = LearnedPositionalEmbedding(total_tokens, config.d_model)
        elif config.pos_embedding_type == "sinusoidal":
            self.pos_embed = SinusoidalPositionalEmbedding(total_tokens, config.d_model)
        elif config.pos_embedding_type == "wavelength":
            assert config.wavelengths is not None
            self.pos_embed = WavelengthAwarePositionalEncoding(
                wavelengths=config.wavelengths,
                d_model=config.d_model,
                group_size=config.group_size,
            )
        else:
            raise ValueError(f"Unknown pos_embedding_type: {config.pos_embedding_type}")

        self.dropout = nn.Dropout(p=config.dropout)

    def forward(self, x: Tensor) -> Tensor:
        """Tokenises input volume [B, C, D, H, W] to sequence [B, 1 + T, d_model]."""
        tokens = self.patch_embed(x)  # [B, T, d_model]
        b = tokens.size(0)

        # Prepend CLS token: [B, 1, d_model]
        cls_tokens = self.cls_token.expand(b, -1, -1)
        x_seq = torch.cat((cls_tokens, tokens), dim=1)  # [B, 1 + T, d_model]

        # Add positional embedding & token dropout
        x_seq = self.pos_embed(x_seq)
        return self.dropout(x_seq)


class CNNToTokenAdapter(nn.Module):
    """Adapts 3D-CNN feature representations to Vision Transformer sequence tokens.

    Implements Spec Section 06 step 2:
    Takes CNN feature tensor [B, C, D', H', W'], averages over (H', W')
    -> [B, C, D'] -> groups spectral slices into tokens of size group_size
    -> [B, T, C * group_size] -> Linear projection to d_model.
    """

    def __init__(
        self,
        in_channels: int = 64,
        spectral_dim: int = 16,
        group_size: int = 4,
        d_model: int = 128,
        spatial_pooling: Literal["avg", "center"] = "avg",
    ) -> None:
        super().__init__()
        self.in_channels = in_channels
        self.spectral_dim = spectral_dim
        self.group_size = group_size
        self.d_model = d_model
        self.spatial_pooling = spatial_pooling

        if spectral_dim % group_size != 0:
            raise InvalidDimensionError(
                f"spectral_dim ({spectral_dim}) must be divisible by group_size ({group_size})"
            )
        self.num_tokens = spectral_dim // group_size

        self.proj = nn.Linear(in_channels * group_size, d_model)
        self.norm = nn.LayerNorm(d_model)

    def forward(self, x: Tensor) -> Tensor:
        """Converts CNN features [B, C, D', H', W'] into tokens [B, T, d_model]."""
        if x.dim() != 5:
            raise InvalidDimensionError(
                f"CNNToTokenAdapter expects 5D tensor [B, C, D, H, W], got rank {x.dim()} ({list(x.shape)})"
            )

        b, c, d, h, w = x.shape
        if c != self.in_channels:
            raise InvalidDimensionError(
                f"Expected feature channels {self.in_channels}, got {c}"
            )
        if d != self.spectral_dim:
            raise InvalidDimensionError(
                f"Expected spectral dimension {self.spectral_dim}, got {d}"
            )

        # 1. Spatial reduction
        if self.spatial_pooling == "avg":
            # Global average pool over spatial dimensions (H, W) -> [B, C, D]
            feat_reduced = x.mean(dim=(-2, -1))
        elif self.spatial_pooling == "center":
            # Extract centre spatial pixel -> [B, C, D]
            feat_reduced = x[:, :, :, h // 2, w // 2]
        else:
            raise ValueError(f"Unknown spatial_pooling mode: {self.spatial_pooling}")

        # 2. Reshape and group spectral slices: [B, C, T, g] -> permute to [B, T, C * g]
        t = self.num_tokens
        g = self.group_size
        feat_grouped = feat_reduced.view(b, c, t, g).permute(0, 2, 1, 3).contiguous()
        feat_flat = feat_grouped.view(b, t, c * g)

        # 3. Linear projection to d_model and LayerNorm
        tokens = self.proj(feat_flat)
        return self.norm(tokens)
