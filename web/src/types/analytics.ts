/**
 * Types for GIS Analytics, Acreage breakdowns, and Farm Health KPI summaries.
 */

export interface AcreageBreakdown {
  totalAcres: number;
  healthyAcres: number;
  stressedAcres: number;
  diseasedAcres: number;
  healthyPct: number;
  stressedPct: number;
  diseasedPct: number;
}

export interface StateAcreageItem {
  state: "healthy" | "stressed" | "diseased";
  label: string;
  acres: number;
  percentage: number;
  color: string;
}

export interface SpectralAnomaly {
  id: string;
  label: string;
  wavelength_nm: number;
  delta: number;
  severity: "low" | "medium" | "high";
  affectedAcres: number;
}

export interface AnalyticsSummaryData {
  sceneId: string;
  farmId: string;
  timestamp: string;
  forecastHorizonDays: number;
  totalAcres: number;
  acresAtRisk: number;
  meanRisk: number;
  meanUncertainty: number;
  hotspot5AcreDetected: boolean;
  hotspotAcres: number;
  breakdown: AcreageBreakdown;
  distribution: StateAcreageItem[];
  anomalies: SpectralAnomaly[];
}
