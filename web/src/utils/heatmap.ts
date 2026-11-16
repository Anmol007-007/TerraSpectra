/**
 * Color scale utilities and geometry mapping for hyperspectral prediction heatmaps.
 */

import type { PredictionCell } from "../types/heatmap";

export interface RGBAColor {
  r: number;
  g: number;
  b: number;
  a: number;
}

/**
 * Maps risk probability (0.0 - 1.0) to an RGBA tuple [0..255, 0..255, 0..255, 0..255].
 * - 0.00 - 0.25: Emerald Green (Healthy)
 * - 0.25 - 0.60: Amber/Yellow (Pre-symptomatic stress, 21-day window)
 * - 0.60 - 0.85: Crimson Red (High risk / early blight)
 * - 0.85 - 1.00: Dark Maroon Red (Severe fungal disease)
 */
export function riskToRgba(
  risk: number,
  opacity: number = 0.85,
): [number, number, number, number] {
  const alpha = Math.max(0, Math.min(255, Math.round(opacity * 255)));
  const clamped = Math.max(0, Math.min(1, risk));

  let r: number, g: number, b: number;

  if (clamped < 0.25) {
    // Green -> Light Green/Yellow
    const t = clamped / 0.25;
    r = Math.round(16 + t * (120 - 16));
    g = Math.round(185 + t * (210 - 185));
    b = Math.round(129 - t * (129 - 40));
  } else if (clamped < 0.60) {
    // Yellow -> Amber
    const t = (clamped - 0.25) / 0.35;
    r = Math.round(245 + t * (245 - 245));
    g = Math.round(200 - t * (200 - 158));
    b = Math.round(40 - t * (40 - 11));
  } else if (clamped < 0.85) {
    // Amber -> Red
    const t = (clamped - 0.60) / 0.25;
    r = Math.round(245 - t * (245 - 239));
    g = Math.round(158 - t * (158 - 68));
    b = Math.round(11 + t * (68 - 11));
  } else {
    // Red -> Dark Burgundy
    const t = (clamped - 0.85) / 0.15;
    r = Math.round(239 - t * (239 - 127));
    g = Math.round(68 - t * (68 - 29));
    b = Math.round(68 - t * (68 - 29));
  }

  return [r, g, b, alpha];
}

/**
 * Filter cells according to the user-selected risk threshold.
 */
export function filterCellsByThreshold(
  cells: PredictionCell[],
  threshold: number,
): PredictionCell[] {
  return cells.filter((c) => c.risk >= threshold);
}

/**
 * Convert geographic coordinates (lon, lat) to raster grid indices (r, c).
 */
export function geoToCellIndex(
  lon: number,
  lat: number,
  bounds: [number, number, number, number],
  gridShape: [number, number],
): { r: number; c: number } | null {
  const [minLon, minLat, maxLon, maxLat] = bounds;
  const [rows, cols] = gridShape;
  if (lon < minLon || lon > maxLon || lat < minLat || lat > maxLat) {
    return null;
  }
  const colFraction = (lon - minLon) / (maxLon - minLon);
  const rowFraction = (maxLat - lat) / (maxLat - minLat);
  const c = Math.min(cols - 1, Math.max(0, Math.floor(colFraction * cols)));
  const r = Math.min(rows - 1, Math.max(0, Math.floor(rowFraction * rows)));
  return { r, c };
}

/**
 * Generate 5-point closed polygon coordinates for a 30m GSD grid pixel.
 */
export function cellToPolygon(
  cell: PredictionCell,
  cellSizeM: number = 30,
): [number, number][] {
  const latM = 111320;
  const lonM = 111320 * Math.cos((cell.lat * Math.PI) / 180);
  const halfLon = (cellSizeM / 2) / lonM;
  const halfLat = (cellSizeM / 2) / latM;
  return [
    [cell.lon - halfLon, cell.lat - halfLat],
    [cell.lon + halfLon, cell.lat - halfLat],
    [cell.lon + halfLon, cell.lat + halfLat],
    [cell.lon - halfLon, cell.lat + halfLat],
    [cell.lon - halfLon, cell.lat - halfLat],
  ];
}
