"""Area conversion helpers.

All geospatial area calculations must go through this module.
Units:
    - Area: acres (1 acre = 4046.8564 m²)
    - GSD: metres
"""

from __future__ import annotations

from terraspectra.core.constants import ACRES_PER_M2, GSD_M

M2_PER_ACRE: float = 1.0 / ACRES_PER_M2


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
    return area_acres * M2_PER_ACRE


def pixels_to_m2(n_pixels: int | float, gsd_m: float = GSD_M) -> float:
    """Calculate square metres corresponding to a pixel count given GSD.

    Args:
        n_pixels: Number of pixels.
        gsd_m: Ground sampling distance in metres per pixel edge.

    Returns:
        Area in square metres.
    """
    return float(n_pixels) * (gsd_m ** 2)


def pixels_to_acres(n_pixels: int | float, gsd_m: float = GSD_M) -> float:
    """Convert a pixel count to acres given the ground sampling distance.

    Args:
        n_pixels: Number of pixels.
        gsd_m: Ground sampling distance in metres per pixel edge.

    Returns:
        Area in acres.
    """
    return m2_to_acres(pixels_to_m2(n_pixels, gsd_m))


def acres_to_pixels(area_acres: float, gsd_m: float = GSD_M) -> float:
    """Convert an area in acres to equivalent pixel count at given GSD.

    Args:
        area_acres: Area in acres.
        gsd_m: Ground sampling distance in metres per pixel.

    Returns:
        Pixel count as a float.
    """
    return acres_to_m2(area_acres) / (gsd_m ** 2)
