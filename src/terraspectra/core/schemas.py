"""Pydantic v2 base schemas shared across modules."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class _Base(BaseModel):
    """Shared base model: forbid extra fields, use attribute access."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class BandInfo(_Base):
    """Wavelength metadata for a single spectral band."""

    index: int
    wavelength_nm: float
    is_valid: bool = True
