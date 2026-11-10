"""Area conversion helpers.

All geo math must go through this module so it can be tested centrally.
Units:
    - Reflectance: 0-1 float32
    - Wavelengths: nm
    - Area: acres (1 acre = 4046.8564 m2)
"""

from __future__ import annotations

from terraspectra.core.constants import ACRES_PER_M2, GSD_M

# 1 acre = 4046.8564 m2 (SI definition)
_M2_PER_ACRE: float = 1.0 / ACRES_PER_M2


def m2_to_acres(area_m2: float) -> float:
    """Convert square metres to acres.

    Args:
        area_m2: Area in square metres.

    Returns:
        Area in acres.
    """
    return area_m2 * ACRES_PER_M2


def acres_to_m2(area_acres: float) -> float:
    """Convert acres to square metres.

    Args:
        area_acres: Area in acres.

    Returns:
        Area in square metres.
    """
    return area_acres * _M2_PER_ACRE


def pixels_to_acres(n_pixels: int, gsd_m: float = GSD_M) -> float:
    """Convert a pixel count to acres given the ground sampling distance.

    Args:
        n_pixels: Number of pixels.
        gsd_m: Ground sampling distance in metres per pixel.

    Returns:
        Area in acres.
    """
    return m2_to_acres(n_pixels * gsd_m**2)
