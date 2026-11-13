/**
 * Deck.gl layer registry for assembling and toggling GIS layers.
 */

import { GeoJsonLayer } from "@deck.gl/layers";
import type { LayersList } from "@deck.gl/core";
import { MOCK_FARM_BOUNDARY, MOCK_PARCELS } from "./farmBoundary";

export interface LayerVisibility {
  farmBoundary: boolean;
  parcels: boolean;
  heatmap: boolean;
  zones: boolean;
  uncertainty: boolean;
}

export const DEFAULT_LAYER_VISIBILITY: LayerVisibility = {
  farmBoundary: true,
  parcels: true,
  heatmap: true,
  zones: true,
  uncertainty: false,
};

export function buildDeckLayers(
  visibility: LayerVisibility = DEFAULT_LAYER_VISIBILITY,
  opacity: number = 0.85,
): LayersList {
  const layers: LayersList = [];

  // 1. 1,000-acre Farm Outer Boundary Layer
  if (visibility.farmBoundary) {
    layers.push(
      new GeoJsonLayer({
        id: "layer-farm-boundary",
        data: MOCK_FARM_BOUNDARY as any,
        filled: true,
        stroked: true,
        getFillColor: [91, 192, 190, 25], // Subdued cyan wash
        getLineColor: [91, 192, 190, 255], // Crisp cyan outline
        getLineWidth: 3,
        lineWidthUnits: "pixels",
        pickable: true,
      })
    );
  }

  // 2. Agricultural Parcels / Fields Layer
  if (visibility.parcels) {
    layers.push(
      new GeoJsonLayer({
        id: "layer-parcels",
        data: MOCK_PARCELS as any,
        filled: false,
        stroked: true,
        getLineColor: [248, 250, 252, 160], // Thin white boundary lines
        getLineWidth: 1.5,
        lineWidthUnits: "pixels",
        dashJustified: true,
        getDashArray: [4, 4],
        pickable: true,
      })
    );
  }

  return layers;
}
