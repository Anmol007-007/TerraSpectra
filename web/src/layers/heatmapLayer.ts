/**
 * Deck.gl GridCellLayer for rendering hyperspectral disease risk heatmap.
 */

import { GridCellLayer } from "@deck.gl/layers";
import type { PredictionCell } from "../types/heatmap";
import { riskToRgba } from "../utils/heatmap";

export interface HeatmapLayerOptions {
  id?: string;
  data: PredictionCell[];
  opacity?: number;
  riskThreshold?: number;
  cellSize?: number; // Size in meters
  elevationScale?: number;
  onHover?: (info: { object?: PredictionCell; x: number; y: number }) => void;
}

export function createHeatmapLayer({
  id = "layer-disease-heatmap",
  data,
  opacity = 0.85,
  riskThreshold = 0.0,
  cellSize = 30, // 30m Hyperion GSD
  elevationScale = 50,
  onHover,
}: HeatmapLayerOptions): GridCellLayer {
  // Filter by threshold
  const filteredData = riskThreshold > 0 ? data.filter((c) => c.risk >= riskThreshold) : data;

  return new GridCellLayer<PredictionCell>({
    id,
    data: filteredData,
    pickable: true,
    extruded: true,
    cellSize,
    elevationScale,
    getPosition: (d: PredictionCell) => [d.lon, d.lat],
    getFillColor: (d: PredictionCell) => riskToRgba(d.risk, opacity),
    getElevation: (d: PredictionCell) => d.risk * 10,
    updateTriggers: {
      getFillColor: [opacity],
      getElevation: [riskThreshold],
    },
    onHover: onHover
      ? (info) => {
          const obj = (typeof info.object === "object" && info.object !== null)
            ? (info.object as PredictionCell)
            : undefined;
          onHover({ object: obj, x: info.x, y: info.y });
        }
      : undefined,
  });
}
