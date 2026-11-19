/**
 * Deck.gl layer for Ground Control Point (GCP) markers to validate spatial alignment.
 */

import { ScatterplotLayer } from "@deck.gl/layers";
import gcpFixtures from "../tests/fixtures/gcp_fixtures.json";

export interface GCPPoint {
  id: string;
  name: string;
  row: number;
  col: number;
  lon: number;
  lat: number;
}

export interface GCPLayerOptions {
  id?: string;
  visible?: boolean;
  onHover?: (info: { object?: GCPPoint; x: number; y: number }) => void;
  onClick?: (info: { object?: GCPPoint; x: number; y: number }) => void;
}

export function createGCPLayer({
  id = "layer-gcp-markers",
  visible = true,
  onHover,
  onClick,
}: GCPLayerOptions = {}): ScatterplotLayer {
  return new ScatterplotLayer<GCPPoint>({
    id,
    data: gcpFixtures.gcps as GCPPoint[],
    visible,
    pickable: true,
    opacity: 0.95,
    stroked: true,
    filled: true,
    radiusScale: 1,
    radiusMinPixels: 6,
    radiusMaxPixels: 15,
    lineWidthMinPixels: 2,
    getPosition: (d: GCPPoint) => [d.lon, d.lat],
    getRadius: () => 15, // 15m radius (half of 30m GSD)
    getFillColor: (d: GCPPoint) =>
      d.id === "CENTER" ? [239, 68, 68, 220] : [91, 192, 190, 220], // Red for Center, Cyan for Corners
    getLineColor: [255, 255, 255, 255],
    onHover: onHover as any,
    onClick: onClick as any,
  });
}
