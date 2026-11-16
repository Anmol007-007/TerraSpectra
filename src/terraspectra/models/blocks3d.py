"""3D-CNN building blocks for volumetric hyperspectral patch processing.

Provides modular PyTorch 3D layers including Conv3DBlock, ResidualBlock3D,
SE Spectral Attention, Stem, and Pooling layers.
"""

from __future__ import annotations

from typing import Union

import torch
import torch.nn as nn
from torch import Tensor


class Conv3DBlock(nn.Module):
    """Standard 3D convolutional block with Batch Normalization and GELU activation.

    Accepts 5D tensors of shape [Batch, Channels, Depth (Spectral), Height, Width].
    """

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: Union[int, tuple[int, int, int]] = 3,
        stride: Union[int, tuple[int, int, int]] = 1,
        padding: Union[int, tuple[int, int, int]] = 1,
        bias: bool = False,
    ) -> None:
        super().__init__()
        self.conv = nn.Conv3d(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            stride=stride,
            padding=padding,
            bias=bias,
        )
        self.bn = nn.BatchNorm3d(out_channels)
        self.act = nn.GELU()

    def forward(self, x: Tensor) -> Tensor:
        return self.act(self.bn(self.conv(x)))


class SESpectralAttention(nn.Module):
    """Squeeze-and-Excitation attention targeting the spectral-spatial feature channels.

    Computes channel-wise gating recalibration weights to prioritize
    informative spectral bands (e.g. red-edge shifts).
    """

    def __init__(self, channels: int, reduction: int = 4) -> None:
        super().__init__()
        mid_channels = max(channels // reduction, 4)
        self.fc = nn.Sequential(
            nn.Linear(channels, mid_channels, bias=False),
            nn.GELU(),
            nn.Linear(mid_channels, channels, bias=False),
            nn.Sigmoid(),
        )

    def forward(self, x: Tensor) -> Tensor:
        # x shape: [B, C, D, H, W]
        b, c, _, _, _ = x.shape
        # Squeeze spatial and spectral dims via global average pooling
        y = x.view(b, c, -1).mean(dim=-1)  # [B, C]
        scale = self.fc(y).view(b, c, 1, 1, 1)  # [B, C, 1, 1, 1]
        return x * scale


class ResidualBlock3D(nn.Module):
    """Residual block with 3D convolutions and optional SE spectral attention.

    Supports downsampling via stride on spectral and/or spatial dimensions.
    """

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        stride: Union[int, tuple[int, int, int]] = 1,
        use_se: bool = True,
        dropout: float = 0.0,
    ) -> None:
        super().__init__()
        self.conv1 = Conv3DBlock(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=3,
            stride=stride,
            padding=1,
            bias=False,
        )
        self.conv2 = nn.Conv3d(
            in_channels=out_channels,
            out_channels=out_channels,
            kernel_size=3,
            stride=1,
            padding=1,
            bias=False,
        )
        self.bn2 = nn.BatchNorm3d(out_channels)
        self.se = SESpectralAttention(out_channels) if use_se else nn.Identity()
        self.dropout = nn.Dropout3d(p=dropout) if dropout > 0.0 else nn.Identity()
        self.act = nn.GELU()

        # Shortcut projection if dimension or stride changes
        stride_tuple = (stride, stride, stride) if isinstance(stride, int) else stride
        if in_channels != out_channels or any(s != 1 for s in stride_tuple):
            self.shortcut = nn.Sequential(
                nn.Conv3d(
                    in_channels=in_channels,
                    out_channels=out_channels,
                    kernel_size=1,
                    stride=stride,
                    bias=False,
                ),
                nn.BatchNorm3d(out_channels),
            )
        else:
            self.shortcut = nn.Identity()

    def forward(self, x: Tensor) -> Tensor:
        res = self.shortcut(x)
        out = self.conv1(x)
        out = self.bn2(self.conv2(out))
        out = self.se(out)
        out = self.dropout(out)
        return self.act(out + res)


class StemBlock3D(nn.Module):
    """Initial feature extraction stem for single-channel hyperspectral cubes.

    Projects [B, 1, D, H, W] tensor into base feature channels with 3D kernel.
    """

    def __init__(
        self,
        in_channels: int = 1,
        out_channels: int = 16,
        kernel_size: tuple[int, int, int] = (3, 3, 3),
    ) -> None:
        super().__init__()
        padding = tuple(k // 2 for k in kernel_size)
        self.stem = nn.Sequential(
            nn.Conv3d(
                in_channels=in_channels,
                out_channels=out_channels,
                kernel_size=kernel_size,
                stride=1,
                padding=padding,
                bias=False,
            ),
            nn.BatchNorm3d(out_channels),
            nn.GELU(),
        )

    def forward(self, x: Tensor) -> Tensor:
        return self.stem(x)


class SpectralPooling(nn.Module):
    """Pools/downsamples only the spectral (depth) dimension while preserving spatial layout."""

    def __init__(self, pool_factor: int = 2) -> None:
        super().__init__()
        self.pool = nn.MaxPool3d(kernel_size=(pool_factor, 1, 1), stride=(pool_factor, 1, 1))

    def forward(self, x: Tensor) -> Tensor:
        return self.pool(x)


class GlobalPoolingHead(nn.Module):
    """Adaptive 3D average pooling collapsing (D, H, W) to a 1D feature vector."""

    def __init__(self) -> None:
        super().__init__()
        self.pool = nn.AdaptiveAvgPool3d((1, 1, 1))
        self.flatten = nn.Flatten(start_dim=1)

    def forward(self, x: Tensor) -> Tensor:
        return self.flatten(self.pool(x))


def init_weights_3d(module: nn.Module) -> None:
    """Initialize weights for 3D CNN modules using Kaiming normal distribution."""
    if isinstance(module, nn.Conv3d):
        nn.init.kaiming_normal_(module.weight, mode="fan_out", nonlinearity="relu")
        if module.bias is not None:
            nn.init.constant_(module.bias, 0.0)
    elif isinstance(module, nn.BatchNorm3d):
        nn.init.constant_(module.weight, 1.0)
        nn.init.constant_(module.bias, 0.0)
    elif isinstance(module, nn.Linear):
        nn.init.trunc_normal_(module.weight, std=0.02)
        if module.bias is not None:
            nn.init.constant_(module.bias, 0.0)
