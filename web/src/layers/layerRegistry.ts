/**
 * Deck.gl layer registry for assembling and toggling GIS layers.
 */

import { GeoJsonLayer } from "@deck.gl/layers";
import type { LayersList } from "@deck.gl/core";
import { MOCK_FARM_BOUNDARY, MOCK_PARCELS } from "./farmBoundary";
import { createPixelGridLayer } from "./pixelGridLayer";
import { createGCPLayer } from "./gcpLayer";
import mockPredictionData from "../api/mocks/farm_001_result.json";
import type { FarmPredictionResult, PredictionCell } from "../types/heatmap";

const MOCK_RESULT = mockPredictionData as unknown as FarmPredictionResult;

export interface LayerVisibility {
  farmBoundary: boolean;
  parcels: boolean;
  heatmap: boolean;
  zones: boolean;
  uncertainty: boolean;
  gcps?: boolean;
}

export const DEFAULT_LAYER_VISIBILITY: LayerVisibility = {
  farmBoundary: true,
  parcels: true,
  heatmap: true,
  zones: true,
  uncertainty: false,
  gcps: false,
};

export interface DeckLayersOptions {
  visibility?: LayerVisibility;
  opacity?: number;
  riskThreshold?: number;
  cells?: PredictionCell[];
  selectedCell?: PredictionCell | null;
  hoveredCell?: PredictionCell | null;
  onHoverCell?: (info: { object?: PredictionCell; x: number; y: number }) => void;
  onClickCell?: (info: { object?: PredictionCell; x: number; y: number }) => void;
}

export function buildDeckLayers(
  optionsOrVisibility: LayerVisibility | DeckLayersOptions = DEFAULT_LAYER_VISIBILITY,
  opacityParam: number = 0.85,
  riskThresholdParam: number = 0.0,
  cellsParam: PredictionCell[] = MOCK_RESULT.cells,
): LayersList {
  // Support both object options and legacy argument list
  const opts: DeckLayersOptions =
    "farmBoundary" in optionsOrVisibility
      ? {
          visibility: optionsOrVisibility,
          opacity: opacityParam,
          riskThreshold: riskThresholdParam,
          cells: cellsParam,
        }
      : optionsOrVisibility;

  const visibility = opts.visibility || DEFAULT_LAYER_VISIBILITY;
  const opacity = opts.opacity ?? 0.85;
  const riskThreshold = opts.riskThreshold ?? 0.0;
  const cells = opts.cells || MOCK_RESULT.cells;

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

  // 3. Interactive 3D Disease Risk Pixel Grid Layer
  if (visibility.heatmap && cells.length > 0) {
    layers.push(
      createPixelGridLayer({
        id: "layer-disease-heatmap",
        data: cells,
        opacity,
        riskThreshold,
        selectedCell: opts.selectedCell,
        hoveredCell: opts.hoveredCell,
        onHover: opts.onHoverCell,
        onClick: opts.onClickCell,
        elevationScale: 40,
      })
    );
  }

  // 4. Ground Control Points (GCP) Calibration Markers Layer
  if (visibility.gcps) {
    layers.push(
      createGCPLayer({
        id: "layer-gcp-markers",
      })
    );
  }

  return layers;
}
