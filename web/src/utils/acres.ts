import { ACRES_PER_M2, M2_PER_ACRE, GSD_METRES } from "./constants";
import type { AcreageBreakdown, StateAcreageItem } from "../types/analytics";
import { RISK_COLORS } from "./tokens";

export function m2ToAcres(areaM2: number): number {
  return areaM2 * ACRES_PER_M2;
}

export function acresToM2(areaAcres: number): number {
  return areaAcres * M2_PER_ACRE;
}

export function pixelsToAcres(pixelCount: number, gsdM: number = GSD_METRES): number {
  return m2ToAcres(pixelCount * gsdM * gsdM);
}

export function acresToPixels(areaAcres: number, gsdM: number = GSD_METRES): number {
  return acresToM2(areaAcres) / (gsdM * gsdM);
}

/**
 * Computes exact acreage and percentage breakdowns from cell state classifications.
 * State mapping: 0 = healthy, 1 = stressed (pre-symptomatic ~21d), 2 = diseased.
 *
 * @param cells Array of objects containing cell state { state: 0 | 1 | 2 }
 * @param gsdM Ground sampling distance in metres (default 30m)
 */
export function computeAcreageFromCells(
  cells: Array<{ state: number }>,
  gsdM: number = GSD_METRES
): AcreageBreakdown {
  const total = cells.length;
  if (total === 0) {
    return {
      totalAcres: 0,
      healthyAcres: 0,
      stressedAcres: 0,
      diseasedAcres: 0,
      healthyPct: 0,
      stressedPct: 0,
      diseasedPct: 0,
    };
  }

  let healthyCount = 0;
  let stressedCount = 0;
  let diseasedCount = 0;

  for (const cell of cells) {
    if (cell.state === 0) healthyCount++;
    else if (cell.state === 1) stressedCount++;
    else if (cell.state === 2) diseasedCount++;
  }

  const totalAcres = Number(pixelsToAcres(total, gsdM).toFixed(2));
  const healthyAcres = Number(pixelsToAcres(healthyCount, gsdM).toFixed(2));
  const stressedAcres = Number(pixelsToAcres(stressedCount, gsdM).toFixed(2));
  const diseasedAcres = Number(pixelsToAcres(diseasedCount, gsdM).toFixed(2));

  return {
    totalAcres,
    healthyAcres,
    stressedAcres,
    diseasedAcres,
    healthyPct: Number(((healthyCount / total) * 100).toFixed(1)),
    stressedPct: Number(((stressedCount / total) * 100).toFixed(1)),
    diseasedPct: Number(((diseasedCount / total) * 100).toFixed(1)),
  };
}

/**
 * Formats acreage breakdown into chart distribution items.
 */
export function getDistributionFromBreakdown(breakdown: AcreageBreakdown): StateAcreageItem[] {
  return [
    {
      state: "healthy",
      label: "Healthy Crop",
      acres: breakdown.healthyAcres,
      percentage: breakdown.healthyPct,
      color: RISK_COLORS.HEALTHY,
    },
    {
      state: "stressed",
      label: "Pre-Symptomatic Stress (~21d)",
      acres: breakdown.stressedAcres,
      percentage: breakdown.stressedPct,
      color: RISK_COLORS.STRESSED,
    },
    {
      state: "diseased",
      label: "Visible Blight",
      acres: breakdown.diseasedAcres,
      percentage: breakdown.diseasedPct,
      color: RISK_COLORS.DISEASED,
    },
  ];
}
