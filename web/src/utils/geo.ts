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
