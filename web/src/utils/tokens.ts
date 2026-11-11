/**
 * Design tokens for TerraSpectra GIS Dashboard.
 */

export const RISK_COLORS = {
  HEALTHY: "#10b981",    // Green (< 0.25 risk)
  STRESSED: "#f59e0b",   // Amber (0.25 - 0.60 risk)
  DISEASED: "#ef4444",   // Red (> 0.60 risk, 5-acre blight zone)
  NODATA: "#64748b",     // Muted slate
} as const;

export const RISK_THRESHOLDS = {
  PRE_SYMPTOMATIC: 0.35,
  VISIBLE_SYMPTOMS: 0.60,
  HIGH_RISK_ACTION: 0.75,
} as const;

export const MAP_DEFAULTS = {
  DEFAULT_LAT: 28.62,
  DEFAULT_LON: 77.10,
  DEFAULT_ZOOM: 14.5,
  PITCH_3D: 45,
  BEARING: -15,
} as const;
