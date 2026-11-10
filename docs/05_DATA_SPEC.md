# 05 — Data Specification
## Cube conventions
- In-memory cube: `float32 [B, H, W]` (bands first). GeoTIFF: multi-band, band i = wavelength i. HDF5: dataset `/cube` chunked `(B_chunk=32, 128, 128)`, attrs: `wavelengths_nm`, `crs`, `transform`, `gsd_m`, `acquired` (ISO date), `sensor`.
- Default synthetic: **B=224** bands, 400–2500 nm (~9.4 nm step), GSD **30 m**, CRS **EPSG:32643** (UTM 43N, configurable), nodata `-9999`.
- Scenes: `farm` 128×128 px (farm mask ≈ 67×67 px ≈ 1,000 acres), `large` 2048×2048 px (tiling/memory tests), time series of T=12 acquisitions, 5–7 day revisit.
## Bad bands (dropped before PCA)
~1350–1460 nm, ~1790–1960 nm, >2400 nm, plus any band with >20% NaN. Keep a `valid_band_mask`.
## Spectral indices
NDVI=(R800−R670)/(R800+R670) · PRI=(R531−R570)/(R531+R570) · NDWI=(R860−R1240)/(R860+R1240) ·
Red-edge position (max 1st derivative 680–750 nm) · CIre=R780/R710−1 · MCARI.
## Preprocessing order
nodata→NaN → bad-band mask → spike removal → Savitzky-Golay smoothing → clip [0,1] → per-band standardisation (streaming Welford stats from TRAIN scenes only) → IncrementalPCA(n=32, whiten optional) → float32.
## Labels
`state` uint8 per pixel: 0 healthy, 1 pre-symptomatic stress, 2 visibly diseased, 255 ignore/invalid.
`severity` float32 [0,1]. `days_to_symptoms` float32 (0–60, NaN if healthy). Forecast label for horizon h: pixel will show visible disease within h days (h ∈ {7,14,21}).
## Synthetic physics (simplified, document the equations in code)
Healthy leaf: chlorophyll absorption at ~450 & 670 nm, green peak 550, red-edge sigmoid ~710 nm, NIR plateau 0.45–0.55, water absorption 970/1200/1450/1940, SWIR dry-matter.
Stress(severity s∈[0,1]): chlorophyll ×(1−0.5s), red-edge shifts ~−8 nm·s (blue shift), PRI ↓, water content ↓ (water features shallower), SWIR ↑ ~+0.04s. Visible symptoms threshold s>=0.6. Severity grows ~logistically over ~21 days from outbreak seed with spatial diffusion; hotspot sized to ≈5 acres (≈22 px).
Noise: gaussian + sensor SNR(λ) lower in SWIR; optional cloud/shadow & dead pixels.
## Splits
Spatial block split (e.g., 64×64 blocks, 70/15/15) with 2-pixel buffer to avoid leakage; temporal split option (train early dates, test later). Persist `splits.json`.
## Catalog
`data/catalog/scenes.json`: `[{scene_id, path, format, bands, shape, crs, bounds_wgs84, acquired, gsd_m, size_mb}]`.
