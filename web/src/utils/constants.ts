/**
 * Geographic and sensor constants for TerraSpectra Web GIS.
 */

// 1 acre = 4046.8564 square metres
export const ACRES_PER_M2 = 1 / 4046.8564;
export const M2_PER_ACRE = 4046.8564;

// Hyperion-like spatial ground sampling distance
export const GSD_METRES = 30.0;
export const PIXEL_AREA_M2 = GSD_METRES * GSD_METRES; // 900 m²
export const PIXEL_AREA_ACRES = PIXEL_AREA_M2 * ACRES_PER_M2; // ≈ 0.22239 acres

// Reference demonstration geometry
export const FARM_TOTAL_ACRES = 1000.0;
export const HOTSPOT_TARGET_ACRES = 5.0;
