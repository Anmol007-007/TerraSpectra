/**
 * Deck.gl layer registry for assembling and toggling GIS layers.
 */

import { GeoJsonLayer } from "@deck.gl/layers";
import type { LayersList } from "@deck.gl/core";
import { MOCK_FARM_BOUNDARY, MOCK_PARCELS } from "./farmBoundary";
import { createHeatmapLayer } from "./heatmapLayer";
import mockPredictionData from "../api/mocks/farm_001_result.json";
import type { FarmPredictionResult, PredictionCell } from "../types/heatmap";

const MOCK_RESULT = mockPredictionData as unknown as FarmPredictionResult;

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
  riskThreshold: number = 0.0,
  cells: PredictionCell[] = MOCK_RESULT.cells,
): LayersList {
  const layers: LayersList = [];

  // 1. 1,000-acre Farm Outer Boundary Layer
  if (visibility.farmBoundary) {
    layers.push(
      new GeoJsonLayer({
        id: "layer-farm-boundary",
        data: MOCK_FARM_BOUNDARY as unknown as GeoJSON.FeatureCollection,
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
        data: MOCK_PARCELS as unknown as GeoJSON.FeatureCollection,
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

  // 3. 3D Disease Risk GridCellLayer
  if (visibility.heatmap && cells.length > 0) {
    layers.push(
      createHeatmapLayer({
        id: "layer-disease-heatmap",
        data: cells,
        opacity,
        riskThreshold,
        cellSize: 30,
        elevationScale: 40,
      })
    );
  }

  return layers;
}
