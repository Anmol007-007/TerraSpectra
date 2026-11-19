/**
 * Geospatial camera utilities: fitBounds calculation and camera navigation.
 */

export interface BoundingBox {
  minLon: number;
  minLat: number;
  maxLon: number;
  maxLat: number;
}

export interface ViewportState {
  longitude: number;
  latitude: number;
  zoom: number;
}

/**
 * Compute center coordinates and approximate zoom level for a geographic bounding box.
 */
export function fitBounds(
  bounds: BoundingBox,
  viewportWidth: number = 800,
  viewportHeight: number = 600,
): ViewportState {
  const { minLon, minLat, maxLon, maxLat } = bounds;
  const lonCenter = (minLon + maxLon) / 2;
  const latCenter = (minLat + maxLat) / 2;

  const lonDiff = Math.abs(maxLon - minLon);
  const latDiff = Math.abs(maxLat - minLat);

  // Web Mercator zoom computation
  const zoomLon = Math.log2((360 * viewportWidth) / (lonDiff * 256));
  const zoomLat = Math.log2((180 * viewportHeight) / (latDiff * 256));

  const zoom = Math.min(zoomLon, zoomLat) - 0.5;

  return {
    longitude: lonCenter,
    latitude: latCenter,
    zoom: Math.max(1, Math.min(20, Math.round(zoom * 10) / 10)),
  };
}

/**
 * Standard bounding box of the demonstration 1,000-acre farm parcel.
 */
export const FARM_BOUNDS: BoundingBox = {
  minLon: 77.0900,
  minLat: 28.6100,
  maxLon: 77.1105,
  maxLat: 28.6285,
};

export interface GCPPoint {
  id: string;
  name: string;
  row: number;
  col: number;
  lon: number;
  lat: number;
}

/**
 * Canonical 5 Ground Control Points (GCPs) for 1,000-acre farm parcel alignment.
 */
export const CANONICAL_GCPS: GCPPoint[] = [
  {
    id: "NW_CORNER",
    name: "Northwest Boundary Corner",
    row: 0,
    col: 0,
    lon: 77.090153,
    lat: 28.6283619,
  },
  {
    id: "NE_CORNER",
    name: "Northeast Boundary Corner",
    row: 0,
    col: 66,
    lon: 77.110347,
    lat: 28.6283619,
  },
  {
    id: "CENTER",
    name: "Farm Geographic Center",
    row: 33,
    col: 33,
    lon: 77.10025,
    lat: 28.61925,
  },
  {
    id: "SW_CORNER",
    name: "Southwest Boundary Corner",
    row: 66,
    col: 0,
    lon: 77.090153,
    lat: 28.6101381,
  },
  {
    id: "SE_CORNER",
    name: "Southeast Boundary Corner",
    row: 66,
    col: 66,
    lon: 77.110347,
    lat: 28.6101381,
  },
];

/**
 * Convert raster pixel indices (row, col) to WGS84 geographic coordinates (lon, lat).
 * Adheres to half-pixel center offset convention (r + 0.5, c + 0.5).
 */
export function pixelToLonLat(
  row: number,
  col: number,
  bounds: BoundingBox = FARM_BOUNDS,
  gridShape: [number, number] = [67, 67],
  centerOffset: boolean = true,
): [number, number] {
  const { minLon, minLat, maxLon, maxLat } = bounds;
  const [numRows, numCols] = gridShape;

  const rEff = row + (centerOffset ? 0.5 : 0.0);
  const cEff = col + (centerOffset ? 0.5 : 0.0);

  const lonStep = (maxLon - minLon) / numCols;
  const latStep = (maxLat - minLat) / numRows;

  const lon = minLon + cEff * lonStep;
  const lat = maxLat - rEff * latStep;

  return [Math.round(lon * 1e7) / 1e7, Math.round(lat * 1e7) / 1e7];
}

/**
 * Convert WGS84 coordinates (lon, lat) to continuous raster pixel indices (row, col).
 */
export function lonLatToPixel(
  lon: number,
  lat: number,
  bounds: BoundingBox = FARM_BOUNDS,
  gridShape: [number, number] = [67, 67],
): [number, number] {
  const { minLon, minLat, maxLon, maxLat } = bounds;
  const [numRows, numCols] = gridShape;

  const c = ((lon - minLon) / (maxLon - minLon)) * numCols - 0.5;
  const r = ((maxLat - lat) / (maxLat - minLat)) * numRows - 0.5;

  return [Math.round(r * 1e6) / 1e6, Math.round(c * 1e6) / 1e6];
}

/**
 * Compute the bounding polygon coordinates for a raster grid cell [row, col]
 * strictly adhering to the half-pixel centering convention.
 */
export function pixelIndexToPolygon(
  row: number,
  col: number,
  bounds: BoundingBox = FARM_BOUNDS,
  gridShape: [number, number] = [67, 67],
): [number, number][] {
  const [centerLon, centerLat] = pixelToLonLat(row, col, bounds, gridShape, true);
  const { minLon, minLat, maxLon, maxLat } = bounds;
  const [rows, cols] = gridShape;
  const halfStepLon = (maxLon - minLon) / (2 * cols);
  const halfStepLat = (maxLat - minLat) / (2 * rows);

  return [
    [centerLon - halfStepLon, centerLat - halfStepLat],
    [centerLon + halfStepLon, centerLat - halfStepLat],
    [centerLon + halfStepLon, centerLat + halfStepLat],
    [centerLon - halfStepLon, centerLat + halfStepLat],
    [centerLon - halfStepLon, centerLat - halfStepLat],
  ];
}
