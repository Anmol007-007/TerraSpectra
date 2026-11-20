/**
 * Deck.gl layer for interactive 30m GSD pixel grid inspection and picking.
 */

import { GridCellLayer } from "@deck.gl/layers";
import type { PickingInfo } from "@deck.gl/core";
import type { PredictionCell } from "../types/heatmap";
import { riskToRgba } from "../utils/heatmap";

export interface PixelGridLayerOptions {
  id?: string;
  data: PredictionCell[];
  opacity?: number;
  riskThreshold?: number;
  selectedCell?: PredictionCell | null;
  hoveredCell?: PredictionCell | null;
  elevationScale?: number;
  onHover?: (info: PickingInfo<PredictionCell>) => void;
  onClick?: (info: PickingInfo<PredictionCell>) => void;
}

export function createPixelGridLayer({
  id = "layer-pixel-grid",
  data,
  opacity = 0.90,
  riskThreshold = 0.0,
  selectedCell = null,
  hoveredCell = null,
  elevationScale = 45,
  onHover,
  onClick,
}: PixelGridLayerOptions): GridCellLayer {
  const filtered = riskThreshold > 0 ? data.filter((c) => c.risk >= riskThreshold) : data;

  return new GridCellLayer<PredictionCell>({
    id,
    data: filtered,
    pickable: true,
    extruded: true,
    cellSize: 30, // 30m Ground Sample Distance
    elevationScale,
    getPosition: (d: PredictionCell) => [d.lon, d.lat],
    getFillColor: (d: PredictionCell) => {
      // Highlight selected or hovered cell
      if (selectedCell && d.r === selectedCell.r && d.c === selectedCell.c) {
        return [111, 255, 233, 255]; // Bright mint cyan highlight
      }
      if (hoveredCell && d.r === hoveredCell.r && d.c === hoveredCell.c) {
        return [255, 255, 255, 240]; // Bright white hover glow
      }
      return riskToRgba(d.risk, opacity);
    },
    getElevation: (d: PredictionCell) => {
      let baseElev = d.risk * 12;
      if (selectedCell && d.r === selectedCell.r && d.c === selectedCell.c) {
        baseElev += 5;
      }
      return baseElev;
    },
    updateTriggers: {
      getFillColor: [opacity, selectedCell?.r, selectedCell?.c, hoveredCell?.r, hoveredCell?.c],
      getElevation: [riskThreshold, selectedCell?.r, selectedCell?.c, elevationScale],
    },
    onHover: onHover ? (info) => onHover(info as PickingInfo<PredictionCell>) : undefined,
    onClick: onClick ? (info) => onClick(info as PickingInfo<PredictionCell>) : undefined,
  });
}
