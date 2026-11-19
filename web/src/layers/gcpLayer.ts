/**
 * Deck.gl layer for Ground Control Point (GCP) markers to validate spatial alignment.
 */

import { ScatterplotLayer } from "@deck.gl/layers";
import type { PickingInfo } from "@deck.gl/core";
import { CANONICAL_GCPS, type GCPPoint } from "../utils/geo";

export type { GCPPoint };

export interface GCPLayerOptions {
  id?: string;
  data?: GCPPoint[];
  visible?: boolean;
  onHover?: (info: PickingInfo<GCPPoint>) => void;
  onClick?: (info: PickingInfo<GCPPoint>) => void;
}

export function createGCPLayer({
  id = "layer-gcp-markers",
  data = CANONICAL_GCPS,
  visible = true,
  onHover,
  onClick,
}: GCPLayerOptions = {}): ScatterplotLayer {
  return new ScatterplotLayer<GCPPoint>({
    id,
    data,
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
    onHover: onHover ? (info) => onHover(info as PickingInfo<GCPPoint>) : undefined,
    onClick: onClick ? (info) => onClick(info as PickingInfo<GCPPoint>) : undefined,
  });
}
