# Changelog

All notable changes to TerraSpectra will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-11-20

### Mid-Project Milestone Release (Weeks 1 & 2)

#### Added
- **Hyperspectral Synthetic Data Pipeline**: Physics-grounded PROSPECT-D leaf reflectance and bad-band masking across 224 bands (400–2500 nm).
- **Out-of-Core Memory Streaming**: Chunked GeoTIFF, HDF5, and `np.memmap` readers maintaining process RSS $< 185$ MB under a 2.0 GB ceiling.
- **Incremental Preprocessing**: Single-pass Welford online normalizer and Incremental PCA (224 to 32 channels) preserving $>99\%$ spectral variance.
- **3D-CNN Feature Extractor**: Volumetric convolutions with Squeeze-and-Excitation (SE) spectral attention, residual connections, and gradient checkpointing.
- **Imbalance-Aware Loss Functions**: Focal Loss ($\gamma = 2.0$), Class-Balanced weights, and Weighted Random Sampling for high-skew agricultural targets.
- **GIS Coordinate Precision & GCPs**: Affine coordinate transforms with $+0.5$ half-pixel centering, 5 canonical ground control points, and sub-millimeter precision.
- **Interactive 3D GIS Dashboard**: Deck.gl 9 + Mapbox GL viewer with 30m GSD pixel grid, 5-acre disease zone identification, Pixel Inspector HUD, and GCP alignment markers.

#### Fixed
- Fixed coordinate alignment by enforcing $+0.5$ half-pixel center offsets in both Python and TypeScript GIS utilities.
- Fixed big-endian byteorder compatibility in raster readers by auto-converting to native byteorder.
- Fixed Windows multiprocessing overhead by auto-tuning DataLoader worker allocations.
- Fixed activation memory bottlenecks via optional gradient checkpointing in deep 3D residual stages.

#### Security & Quality
- Added strict input validation for empty, corrupt, or single-band rasters.
- Passed 68 backend unit tests (`pytest`) and 32 frontend component/integration tests (`vitest`).
- Passed TypeScript strict compiler checks with 0 errors (`tsc --noEmit`).
