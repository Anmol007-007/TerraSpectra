"""Domain models and Pydantic schemas for TerraSpectra."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class _Base(BaseModel):
    """Shared base model: forbid extra fields, use attribute access."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class GeoBounds(_Base):
    """Geographic spatial bounding box coordinates in WGS-84 or projected CRS."""

    west: float = Field(..., description="Westernmost longitude / X min")
    south: float = Field(..., description="Southernmost latitude / Y min")
    east: float = Field(..., description="Easternmost longitude / X max")
    north: float = Field(..., description="Northernmost latitude / Y max")
    crs: str = Field(default="EPSG:4326", description="Coordinate reference system")

    @property
    def tuple(self) -> tuple[float, float, float, float]:
        """Return (west, south, east, north) tuple."""
        return (self.west, self.south, self.east, self.north)


class BandInfo(_Base):
    """Wavelength metadata for a single spectral band."""

    index: int = Field(..., description="0-based channel index in the cube")
    wavelength_nm: float = Field(..., description="Centre wavelength in nanometres")
    fwhm_nm: float | None = Field(default=None, description="Full-width at half-maximum")
    is_valid: bool = Field(default=True, description="False if water vapour or high noise band")


class WavelengthGrid(_Base):
    """Full spectral definition of a sensor or synthetic cube."""

    n_bands: int = Field(..., description="Total count of bands")
    wavelengths_nm: list[float] = Field(..., description="List of band centre wavelengths")
    valid_mask: list[bool] = Field(..., description="Boolean validity flags per band")
