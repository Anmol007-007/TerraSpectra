/**
 * Core domain types for TerraSpectra frontend.
 */

export type PixelState = "healthy" | "stressed" | "diseased";

export interface GeoBounds {
  west: number;
  south: number;
  east: number;
  north: number;
}

export interface RiskZone {
  zone_id: string;
  area_acres: number;
  mean_risk: number;
  lead_time_days: number;
  disease: string;
  recommended_action: string;
  geometry: {
    type: "Polygon" | "MultiPolygon";
    coordinates: number[][][];
  };
}

export interface Anomaly {
  id: string;
  label: string;
  wavelength_nm: number;
  delta: number;
  severity: "low" | "medium" | "high";
}

export interface AnalyticsSummary {
  total_acres: number;
  acres_at_risk: number;
  acres_by_state: {
    healthy: number;
    stressed: number;
    diseased: number;
  };
  anomalies: Anomaly[];
}

export interface PredictionResult {
  scene_id: string;
  model_version: string;
  acquired: string;
  horizon_days: number;
  crs: string;
  gsd_m: number;
  origin: [number, number];
  cell_size_deg: [number, number];
  grid: {
    rows: number;
    cols: number;
    risk: number[][];
    severity: number[][];
    uncertainty: number[][];
    state: number[][];
  };
  zones: {
    type: "FeatureCollection";
    features: Array<{
      type: "Feature";
      geometry: RiskZone["geometry"];
      properties: Omit<RiskZone, "geometry">;
    }>;
  };
  analytics: AnalyticsSummary;
}
