/**
 * TypeScript types for disease prediction heatmap and risk grids.
 */

export type CropState = 0 | 1 | 2; // 0: Healthy, 1: Pre-symptomatic (21d), 2: Visible disease

export interface PredictionCell {
  r: number;
  c: number;
  lon: number;
  lat: number;
  risk: number; // 0.0 - 1.0 probability of disease
  severity: number; // 0.0 - 1.0 lesion intensity
  uncertainty: number; // 0.0 - 1.0 Monte Carlo dropout variance
  state: CropState;
  days_to_symptoms?: number; // Days until visible symptoms (~21 days for state 1)
}

export interface FarmPredictionSummary {
  healthy_pct: number;
  pre_symptomatic_pct: number;
  diseased_pct: number;
  mean_uncertainty: number;
  high_risk_pixel_count: number;
  high_risk_acreage: number;
}

export interface FarmPredictionResult {
  scene_id: string;
  farm_id: string;
  timestamp: string;
  forecast_horizon_days: number;
  grid_shape: [number, number]; // [rows, cols]
  cell_size_m: number; // 30m Hyperion GSD
  bounds: [number, number, number, number]; // [minLon, minLat, maxLon, maxLat]
  hotspot_5acre_detected: boolean;
  hotspot_acres: number;
  summary: FarmPredictionSummary;
  cells: PredictionCell[];
}
