import React from "react";
import DeckGL from "@deck.gl/react";
import type { LayersList } from "@deck.gl/core";

export interface DeckGLOverlayProps {
  viewState: {
    longitude: number;
    latitude: number;
    zoom: number;
    pitch?: number;
    bearing?: number;
  };
  onViewStateChange?: (params: { viewState: any }) => void;
  layers?: LayersList;
  children?: React.ReactNode;
}

export const DeckGLOverlay: React.FC<DeckGLOverlayProps> = ({
  viewState,
  onViewStateChange,
  layers = [],
  children,
}) => {
  return (
    <div className="absolute inset-0 w-full h-full overflow-hidden" data-testid="deckgl-overlay">
      <DeckGL
        viewState={viewState}
        onViewStateChange={onViewStateChange}
        controller={true}
        layers={layers}
      >
        {children}
      </DeckGL>
    </div>
  );
};
