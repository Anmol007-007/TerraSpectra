"""Model zoo: 3D-CNN blocks, SpectralViT, HybridCNNViT, heads, registry."""

from terraspectra.models.blocks3d import (
    Conv3DBlock,
    GlobalPoolingHead,
    ResidualBlock3D,
    SESpectralAttention,
    SpectralPooling,
    StemBlock3D,
    init_weights_3d,
)
from terraspectra.models.cnn3d import (
    CNN3DClassifier,
    CNN3DConfig,
    count_parameters,
    model_summary,
)
from terraspectra.models.registry import ModelRegistry, model_registry

# Register standard architectures
model_registry.register("cnn3d_v1", CNN3DClassifier)

__all__ = [
    "Conv3DBlock",
    "SESpectralAttention",
    "ResidualBlock3D",
    "StemBlock3D",
    "SpectralPooling",
    "GlobalPoolingHead",
    "init_weights_3d",
    "CNN3DConfig",
    "CNN3DClassifier",
    "count_parameters",
    "model_summary",
    "ModelRegistry",
    "model_registry",
]
