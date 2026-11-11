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
