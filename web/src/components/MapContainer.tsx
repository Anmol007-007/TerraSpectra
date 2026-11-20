import React, { useCallback, useMemo, useState } from "react";
import { BaseMap } from "./BaseMap";
import { DeckGLOverlay } from "./DeckGLOverlay";
import { PixelInspector } from "./PixelInspector";
import { Crosshair } from "./Crosshair";
import { CoordinateReadout } from "./CoordinateReadout";
import { buildDeckLayers } from "../layers/layerRegistry";
import { useLayerStore } from "../store/layerStore";
import { FARM_BOUNDS, fitBounds } from "../utils/geo";
import { MAP_DEFAULTS } from "../utils/tokens";
import type { PredictionCell } from "../types/heatmap";

export interface MapViewState {
  longitude: number;
  latitude: number;
  zoom: number;
  pitch: number;
  bearing: number;
}

export const MapContainer: React.FC = () => {
  const initial = fitBounds(FARM_BOUNDS);
  const [viewState, setViewState] = useState<MapViewState>({
    longitude: initial.longitude,
    latitude: initial.latitude,
    zoom: initial.zoom,
    pitch: MAP_DEFAULTS.PITCH_3D,
    bearing: MAP_DEFAULTS.BEARING,
  });

  const {
    visibility,
    heatmapOpacity,
    riskThreshold,
    hoveredCell,
    selectedCell,
    setHoveredCell,
    setSelectedCell,
  } = useLayerStore();

  const handleHoverCell = useCallback(
    (info: { object?: PredictionCell }) => {
      setHoveredCell(info.object || null);
    },
    [setHoveredCell]
  );

  const handleClickCell = useCallback(
    (info: { object?: PredictionCell }) => {
      setSelectedCell(info.object || null);
    },
    [setSelectedCell]
  );

  const layers = useMemo(
    () =>
      buildDeckLayers({
        visibility,
        opacity: heatmapOpacity,
        riskThreshold,
        hoveredCell,
        selectedCell,
        onHoverCell: handleHoverCell,
        onClickCell: handleClickCell,
      }),
    [visibility, heatmapOpacity, riskThreshold, hoveredCell, selectedCell, handleHoverCell, handleClickCell]
  );

  const handleFlyToFarm = () => {
    const target = fitBounds(FARM_BOUNDS);
    setViewState((prev) => ({
      ...prev,
      longitude: target.longitude,
      latitude: target.latitude,
      zoom: target.zoom,
    }));
  };

  const handleZoomToPixel = (lon: number, lat: number) => {
    setViewState((prev) => ({
      ...prev,
      longitude: lon,
      latitude: lat,
      zoom: 16.5,
    }));
  };

  return (
    <div className="relative w-full h-full overflow-hidden" data-testid="map-viewport">
      <BaseMap initialViewState={viewState}>
        <DeckGLOverlay
          viewState={viewState}
          onViewStateChange={(params) => {
            const vs = params.viewState as unknown as MapViewState;
            setViewState(vs);
          }}
          layers={layers}
        />
      </BaseMap>

      {/* Interactive Pixel Inspector Overlay */}
      <div className="absolute top-4 right-4 z-10">
        <PixelInspector onZoomToPixel={handleZoomToPixel} />
      </div>

      {/* Crosshair Alignment Reticle (active when GCP layer or inspector is in use) */}
      <Crosshair visible={!!visibility.gcps} />

      {/* Real-time Coordinate Readout HUD */}
      <div className="absolute bottom-6 left-6 z-10">
        <CoordinateReadout cursorLonLat={[viewState.longitude, viewState.latitude]} />
      </div>

      {/* Fly-to-farm reset camera button */}
      <div className="absolute bottom-6 right-6 z-10">
        <button
          onClick={handleFlyToFarm}
          className="bg-[#1c2541]/95 hover:bg-[#3a506b] text-slate-100 border border-[#5bc0be]/60 px-3 py-2 rounded-lg text-xs font-semibold shadow-xl flex items-center space-x-2 transition-all"
        >
          <span>🎯</span>
          <span>Zoom to 1,000-Acre Farm</span>
        </button>
      </div>
    </div>
  );
};
