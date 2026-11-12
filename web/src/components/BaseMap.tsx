import React, { useState } from "react";
import Map, { NavigationControl, ScaleControl } from "react-map-gl";
import { env } from "../utils/env";
import { MAP_DEFAULTS } from "../utils/tokens";
import "mapbox-gl/dist/mapbox-gl.css";

export type BaseMapStyle = "satellite" | "streets" | "dark";

export interface BaseMapProps {
  initialViewState?: {
    longitude: number;
    latitude: number;
    zoom: number;
    pitch?: number;
    bearing?: number;
  };
  styleType?: BaseMapStyle;
  children?: React.ReactNode;
}

const MAPBOX_STYLES: Record<BaseMapStyle, string> = {
  satellite: "mapbox://styles/mapbox/satellite-streets-v12",
  streets: "mapbox://styles/mapbox/streets-v12",
  dark: "mapbox://styles/mapbox/dark-v11",
};

// Open-source MapLibre/OSM raster style fallback when no Mapbox token is provided
const OPEN_FALLBACK_STYLE = {
  version: 8,
  sources: {
    "osm-tiles": {
      type: "raster",
      tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
      tileSize: 256,
      attribution: "&copy; OpenStreetMap contributors",
    },
  },
  layers: [
    {
      id: "osm-tiles-layer",
      type: "raster",
      source: "osm-tiles",
      minzoom: 0,
      maxzoom: 19,
    },
  ],
};

export const BaseMap: React.FC<BaseMapProps> = ({
  initialViewState = {
    longitude: MAP_DEFAULTS.DEFAULT_LON,
    latitude: MAP_DEFAULTS.DEFAULT_LAT,
    zoom: MAP_DEFAULTS.DEFAULT_ZOOM,
    pitch: MAP_DEFAULTS.PITCH_3D,
    bearing: MAP_DEFAULTS.BEARING,
  },
  styleType = "satellite",
  children,
}) => {
  const [currentStyle, setCurrentStyle] = useState<BaseMapStyle>(styleType);
  const token = env.mapboxToken;
  const isMapbox = Boolean(token) && env.basemap === "mapbox";

  const mapStyle = isMapbox ? MAPBOX_STYLES[currentStyle] : (OPEN_FALLBACK_STYLE as any);

  return (
    <div className="relative w-full h-full" data-testid="base-map-container">
      <Map
        initialViewState={initialViewState}
        style={{ width: "100%", height: "100%" }}
        mapStyle={mapStyle}
        mapboxAccessToken={isMapbox ? token : undefined}
        attributionControl={true}
      >
        <NavigationControl position="top-right" />
        <ScaleControl position="bottom-left" />
        {children}
      </Map>

      {/* Style switcher toggle */}
      <div className="absolute top-4 left-4 z-10 bg-[#1c2541]/90 backdrop-blur border border-[#3a506b] rounded-lg p-1.5 flex space-x-1 shadow-lg text-xs">
        {(["satellite", "streets", "dark"] as BaseMapStyle[]).map((st) => (
          <button
            key={st}
            onClick={() => setCurrentStyle(st)}
            className={`px-2.5 py-1 rounded capitalize font-medium transition-colors ${
              currentStyle === st
                ? "bg-[#5bc0be] text-[#0b132b] font-bold"
                : "text-slate-300 hover:text-white hover:bg-[#3a506b]/50"
            }`}
          >
            {st}
          </button>
        ))}
      </div>
    </div>
  );
};
