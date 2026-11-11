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
