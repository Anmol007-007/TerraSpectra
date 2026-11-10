# 01 — Project Specification (from the Infotact project document)

**Title:** TerraSpectra — Hyperspectral Crop Disease Forecasting
**Domain:** Precision Agriculture & Advanced Computer Vision
**Duration:** 20 days, >= 52 git commits/day (1,040+ commits)

## Problem statement
Traditional satellite crop monitoring uses RGB or simple infrared imagery and only detects disease
after leaves turn yellow/brown — too late to save the harvest. Standard 2D CNNs cannot process the
spectral depth (200+ bands) needed for early detection.

## Use case
An agricultural analyst monitors a **1,000-acre farm** on the TerraSpectra dashboard.
1. System ingests hyperspectral satellite data (200+ bands, invisible to the eye).
2. Backend **3D-CNN + Vision Transformer** analyses subtle chemical changes in chlorophyll reflectance.
3. Dashboard highlights a specific **5-acre zone in red**, predicting a **fungal blight outbreak
   three weeks before visible symptoms**.
4. Enables hyper-targeted, preventative pesticide application.

## Key modules (deliverables)
1. **Geospatial Data Pipeline (Python, Rasterio, GDAL)** — ingest & normalise multi-GB cubes
   (NASA Hyperion / ESA mission formats: HDF5, GeoTIFF).
2. **3D-CNN & ViT Hybrid (PyTorch)** — 3D convs for spatial-spectral features + ViT for deep spectral bands.
3. **Inference API (FastAPI)** — high-throughput REST, chunk/tile massive rasters, GPU.
4. **GIS Dashboard (React & Deck.gl)** — 3D map, disease heatmaps over satellite topography.

## Week-wise plan from the document (mapped to 20 days)
| Doc week | Days | ML / Data pipeline | Frontend / GIS |
|---|---|---|---|
| Week 1 | 1–5 | Rasterio parse mock cubes (HDF5/GeoTIFF); PCA on 200+ bands | React app, Deck.gl + Mapbox base farm layers |
| Week 2 | 6–10 | Hybrid 3D-CNN: classify healthy vs chemically-stressed pixels | Heatmap overlay from mock backend JSON |
| **Mid-Project Review** | 9–10 | **Extraction Audit**: pipeline handles massive memory needs of 3D tensor batches | **GIS Validation**: Deck.gl overlay aligns with real-world GPS coords |
| Week 3 | 11–15 | Integrate ViT self-attention for cross-spectrum correlations | Analytics panel: acreage at risk + chemical anomalies |
| Week 4 | 16–19 | FastAPI + tiling/stitching algorithm | Timeline sliders: historical spectral health |
| **Final Review** | 20 | Fusion of geospatial data engineering + multi-dimensional deep learning | Professional, visually stunning agri-intelligence platform |

## Success criteria
- Pre-symptomatic stress detection F1 >= 0.85 on synthetic held-out spatial blocks.
- Forecast lead time >= 21 days on synthetic outbreaks; zone-level recall >= 0.9.
- Tiled inference matches full-scene inference (max abs diff < 1e-3) on small scenes.
- 2048×2048×224 scene processed on one GPU (or CPU fallback) without OOM using tiling.
- Dashboard heatmap geo-alignment offset < 1 pixel (30 m) in tests.
- Analytics shows acreage at risk and chemical anomalies; timeline slider animates history.
- CI green; coverage >= 85% backend, >= 75% frontend.


## Review Status
Fully reviewed against Infotact Solutions Project Document Vol. II.
