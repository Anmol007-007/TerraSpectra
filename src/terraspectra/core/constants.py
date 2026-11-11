"""Project-wide physical, spectral, and numerical constants."""

from __future__ import annotations

# Spectral wavelength regions (nm)
VNIR_MIN_NM: float = 400.0
VNIR_MAX_NM: float = 1000.0
SWIR_MIN_NM: float = 1000.0
SWIR_MAX_NM: float = 2500.0
RED_EDGE_MIN_NM: float = 680.0
RED_EDGE_MAX_NM: float = 750.0

# Sensor
GSD_M: float = 30.0  # Ground sampling distance in metres (Hyperion-like)
PIXEL_AREA_M2: float = GSD_M ** 2  # 900 m²
ACRES_PER_M2: float = 1.0 / 4046.8564  # 1 acre = 4046.8564 m²
PIXEL_AREA_ACRES: float = PIXEL_AREA_M2 * ACRES_PER_M2  # ≈ 0.2224 acres

# Farm geometry
FARM_ACRES: float = 1000.0
FARM_PIXELS: int = 4497  # ≈ 67×67
HOTSPOT_ACRES: float = 5.0
HOTSPOT_PIXELS: int = 23  # ≈ sqrt(22.5)

# Spectral
N_BANDS: int = 224  # Synthetic band count
WAVELENGTH_MIN_NM: float = 400.0
WAVELENGTH_MAX_NM: float = 2500.0
NODATA: float = -9999.0

# Bad-band ranges (nm) — excluded before PCA
BAD_BAND_RANGES: tuple[tuple[float, float], ...] = (
    (1350.0, 1460.0),  # Water vapour
    (1790.0, 1960.0),  # Water vapour
    (2400.0, 2500.0),  # Noise region
)

# PCA
PCA_N_COMPONENTS: int = 32

# Model
FORECAST_HORIZON_DAYS: int = 21
N_CLASSES: int = 3  # 0=healthy, 1=pre-symptomatic, 2=visibly diseased
CLASS_NAMES: tuple[str, ...] = ("healthy", "stressed", "diseased")

# CRS
DEFAULT_CRS: str = "EPSG:32643"  # UTM Zone 43N

# Diagnostic index wavelength bands (nm)
# NDVI = (R800 - R670) / (R800 + R670)
NDVI_NIR_NM: float = 800.0
NDVI_RED_NM: float = 670.0

# Photochemical Reflectance Index (PRI) = (R531 - R570) / (R531 + R570)
PRI_531_NM: float = 531.0
PRI_570_NM: float = 570.0

# Normalized Difference Water Index (NDWI) = (R860 - R1240) / (R860 + R1240)
NDWI_860_NM: float = 860.0
NDWI_1240_NM: float = 1240.0

# Chlorophyll Red-Edge Index (CIre) = (R780 / R710) - 1
CIRE_780_NM: float = 780.0
CIRE_710_NM: float = 710.0

# Water vapour absorption band detail definitions
WATER_VAPOUR_1400_NM: tuple[float, float] = (1350.0, 1460.0)
WATER_VAPOUR_1900_NM: tuple[float, float] = (1790.0, 1960.0)
SWIR_UPPER_LIMIT_NM: float = 2400.0
