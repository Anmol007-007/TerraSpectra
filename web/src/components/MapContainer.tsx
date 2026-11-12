import React, { useState } from "react";
import { BaseMap } from "./BaseMap";
import { DeckGLOverlay } from "./DeckGLOverlay";
import { MAP_DEFAULTS } from "../utils/tokens";

export const MapContainer: React.FC = () => {
  const [viewState, setViewState] = useState({
    longitude: MAP_DEFAULTS.DEFAULT_LON,
    latitude: MAP_DEFAULTS.DEFAULT_LAT,
    zoom: MAP_DEFAULTS.DEFAULT_ZOOM,
    pitch: MAP_DEFAULTS.PITCH_3D,
    bearing: MAP_DEFAULTS.BEARING,
  });

  return (
    <div className="relative w-full h-full overflow-hidden" data-testid="map-viewport">
      <BaseMap initialViewState={viewState}>
        <DeckGLOverlay
          viewState={viewState}
          onViewStateChange={({ viewState: vs }) => setViewState(vs)}
          layers={[]}
        />
      </BaseMap>
    </div>
  );
};
