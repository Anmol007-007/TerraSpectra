import React, { useState } from "react";
import { BaseMap } from "./BaseMap";
import { DeckGLOverlay } from "./DeckGLOverlay";
import { buildDeckLayers } from "../layers/layerRegistry";
import { useLayerStore } from "../store/layerStore";
import { FARM_BOUNDS, fitBounds } from "../utils/geo";
import { MAP_DEFAULTS } from "../utils/tokens";

export const MapContainer: React.FC = () => {
  const initial = fitBounds(FARM_BOUNDS);
  const [viewState, setViewState] = useState({
    longitude: initial.longitude,
    latitude: initial.latitude,
    zoom: initial.zoom,
    pitch: MAP_DEFAULTS.PITCH_3D,
    bearing: MAP_DEFAULTS.BEARING,
  });

  const { visibility, heatmapOpacity } = useLayerStore();
  const layers = buildDeckLayers(visibility, heatmapOpacity);

  const handleFlyToFarm = () => {
    const target = fitBounds(FARM_BOUNDS);
    setViewState((prev) => ({
      ...prev,
      longitude: target.longitude,
      latitude: target.latitude,
      zoom: target.zoom,
    }));
  };

  return (
    <div className="relative w-full h-full overflow-hidden" data-testid="map-viewport">
      <BaseMap initialViewState={viewState}>
        <DeckGLOverlay
          viewState={viewState}
          onViewStateChange={({ viewState: vs }) => setViewState(vs)}
          layers={layers}
        />
      </BaseMap>

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
