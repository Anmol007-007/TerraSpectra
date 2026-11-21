"""Model zoo: 3D-CNN blocks, SpectralViT, HybridCNNViT, heads, registry."""

from terraspectra.models.attention import (
    DropPath,
    MLPBlock,
    MultiHeadSelfAttention,
    TransformerEncoder,
    TransformerEncoderBlock,
)
from terraspectra.models.blocks3d import (
    Conv3DBlock,
    Dropout3D,
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
    count_parameters as count_parameters_cnn,
    model_summary,
)
from terraspectra.models.registry import ModelRegistry, model_registry
from terraspectra.models.tokens import (
    BandGroupingConfig,
    CNNToTokenAdapter,
    InvalidDimensionError,
    LearnedPositionalEmbedding,
    SinusoidalPositionalEmbedding,
    SpatialSpectralPatchEmbedding,
    SpectralGroupTokenizer,
    WavelengthAwarePositionalEncoding,
)
from terraspectra.models.vit import (
    SpectralViT,
    ViTConfig,
    count_parameters as count_parameters_vit,
)

# Register standard architectures
model_registry.register("cnn3d_v1", CNN3DClassifier)

__all__ = [
    # 3D CNN
    "Conv3DBlock",
    "Dropout3D",
    "SESpectralAttention",
    "ResidualBlock3D",
    "StemBlock3D",
    "SpectralPooling",
    "GlobalPoolingHead",
    "init_weights_3d",
    "CNN3DConfig",
    "CNN3DClassifier",
    "count_parameters_cnn",
    "model_summary",
    # Tokens & Encodings
    "BandGroupingConfig",
    "InvalidDimensionError",
    "LearnedPositionalEmbedding",
    "SinusoidalPositionalEmbedding",
    "WavelengthAwarePositionalEncoding",
    "SpatialSpectralPatchEmbedding",
    "SpectralGroupTokenizer",
    "CNNToTokenAdapter",
    # Attention & Transformer
    "DropPath",
    "MultiHeadSelfAttention",
    "MLPBlock",
    "TransformerEncoderBlock",
    "TransformerEncoder",
    # SpectralViT
    "ViTConfig",
    "SpectralViT",
    "count_parameters_vit",
    # Registry
    "ModelRegistry",
    "model_registry",
]
