"""3D-CNN Classifier model (CNN3D v1) for hyperspectral crop disease detection.

Operates on 3D volumetric patches [B, 1, D, H, W] extracting joint spectral-spatial
features to classify healthy (0), pre-symptomatic stress (1), and diseased (2).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import torch
import torch.nn as nn
from torch import Tensor

from terraspectra.models.blocks3d import (
    GlobalPoolingHead,
    ResidualBlock3D,
    StemBlock3D,
    init_weights_3d,
)


@dataclass
class CNN3DConfig:
    """Configuration hyperparameters for 3D-CNN Classifier."""

    in_channels: int = 1
    depth: int = 32  # Number of spectral bands or PCA components
    patch_size: int = 11  # Spatial patch dimension (H = W)
    base_channels: int = 16
    num_classes: int = 3  # 0: Healthy, 1: Pre-symptomatic (21-day), 2: Diseased
    dropout: float = 0.2
    use_se: bool = True
    stem_kernel: tuple[int, int, int] = (3, 3, 3)
    extra: dict[str, Any] = field(default_factory=dict)


class CNN3DClassifier(nn.Module):
    """3D-CNN Model architecture for hyperspectral volumetric patch classification."""

    def __init__(self, config: CNN3DConfig | None = None, **kwargs: Any) -> None:
        super().__init__()
        if config is None:
            config = CNN3DConfig(**kwargs)
        self.config = config

        c1 = config.base_channels  # 16
        c2 = c1 * 2  # 32
        c3 = c1 * 4  # 64
        c4 = c1 * 8  # 128

        # 1. 3D Convolutional Stem
        self.stem = StemBlock3D(
            in_channels=config.in_channels,
            out_channels=c1,
            kernel_size=config.stem_kernel,
        )

        # 2. Residual Stages with Spectral-Spatial Convolutions & SE Attention
        # Stage 1: Preserves resolution [B, c2, D, H, W]
        self.layer1 = ResidualBlock3D(
            in_channels=c1,
            out_channels=c2,
            stride=(1, 1, 1),
            use_se=config.use_se,
            dropout=config.dropout,
        )

        # Stage 2: Spectral downsampling [B, c3, D/2, H, W]
        self.layer2 = ResidualBlock3D(
            in_channels=c2,
            out_channels=c3,
            stride=(2, 1, 1),
            use_se=config.use_se,
            dropout=config.dropout,
        )

        # Stage 3: Spectral & spatial downsampling [B, c4, D/4, H/2, W/2]
        self.layer3 = ResidualBlock3D(
            in_channels=c3,
            out_channels=c4,
            stride=(2, 2, 2),
            use_se=config.use_se,
            dropout=config.dropout,
        )

        # 3. Global Pooling and Feature Representation
        self.pool = GlobalPoolingHead()

        # 4. Classification Head
        self.classifier = nn.Sequential(
            nn.Dropout(p=config.dropout),
            nn.Linear(c4, config.num_classes),
        )

        # Initialize weights
        self.apply(init_weights_3d)

    def extract_features(self, x: Tensor) -> Tensor:
        """Extract global feature vector for patch."""
        x = self.stem(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        return self.pool(x)

    def forward(self, x: Tensor) -> dict[str, Tensor]:
        """Forward pass.

        Args:
            x: Input tensor of shape [B, 1, D, H, W] or [B, D, H, W].

        Returns:
            Dictionary containing 'logits' [B, num_classes] and 'features' [B, channels].
        """
        if x.ndim == 4:
            x = x.unsqueeze(1)  # Unsqueeze channel dimension -> [B, 1, D, H, W]

        features = self.extract_features(x)
        logits = self.classifier(features)
        return {"logits": logits, "features": features}


def count_parameters(model: nn.Module) -> dict[str, int]:
    """Count trainable and total parameters of a PyTorch module."""
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    return {"trainable": trainable, "total": total}


def model_summary(
    model: nn.Module,
    input_size: tuple[int, ...] = (1, 1, 32, 11, 11),
) -> str:
    """Generate a clean architectural summary string of the model."""
    params = count_parameters(model)
    lines = [
        f"Model: {model.__class__.__name__}",
        "=" * 60,
        f"Input shape:  {input_size}",
        f"Trainable params: {params['trainable']:,}",
        f"Total params:     {params['total']:,}",
        "=" * 60,
    ]
    return "\n".join(lines)
