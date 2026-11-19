import React from "react";
import { useLayerStore } from "../store/layerStore";
import { FARM_BOUNDS, lonLatToPixel } from "../utils/geo";

interface CoordinateReadoutProps {
  cursorLonLat?: [number, number] | null;
}

export const CoordinateReadout: React.FC<CoordinateReadoutProps> = ({ cursorLonLat }) => {
  const { hoveredCell } = useLayerStore();

  let lon = cursorLonLat ? cursorLonLat[0] : hoveredCell ? hoveredCell.lon : 77.10025;
  let lat = cursorLonLat ? cursorLonLat[1] : hoveredCell ? hoveredCell.lat : 28.61925;

  let row: number | null = null;
  let col: number | null = null;

  if (hoveredCell) {
    row = hoveredCell.r;
    col = hoveredCell.c;
  } else if (cursorLonLat) {
    const [r, c] = lonLatToPixel(lon, lat, FARM_BOUNDS, [67, 67]);
    if (r >= 0 && r < 67 && c >= 0 && c < 67) {
      row = Math.floor(r);
      col = Math.floor(c);
    }
  }

  // Web Mercator approximation in meters (EPSG:3857)
  const xMercator = (lon * 20037508.34) / 180;
  const yMercator =
    (Math.log(Math.tan(((90 + lat) * Math.PI) / 360)) / (Math.PI / 180)) * (20037508.34 / 180);

  return (
    <div
      className="bg-[#0b132b]/90 backdrop-blur border border-[#3a506b]/60 px-3 py-1.5 rounded-md text-[11px] font-mono text-slate-300 shadow-lg flex items-center space-x-3 pointer-events-auto"
      data-testid="gis-coordinate-readout"
    >
      <div className="flex items-center space-x-1">
        <span className="text-[#5bc0be] font-bold">WGS84:</span>
        <span>
          {lon.toFixed(6)}°E, {lat.toFixed(6)}°N
        </span>
      </div>

      <div className="hidden sm:flex items-center space-x-1 border-l border-[#3a506b]/60 pl-3">
        <span className="text-slate-400">Raster Pixel:</span>
        <span className={row !== null ? "text-[#6fffe9] font-bold" : "text-slate-500"}>
          {row !== null && col !== null ? `[R:${row}, C:${col}]` : "Outside"}
        </span>
      </div>

      <div className="hidden md:flex items-center space-x-1 border-l border-[#3a506b]/60 pl-3">
        <span className="text-slate-400">EPSG:3857:</span>
        <span>
          {Math.round(xMercator).toLocaleString()}m, {Math.round(yMercator).toLocaleString()}m
        </span>
      </div>

      <div className="flex items-center space-x-1 border-l border-[#3a506b]/60 pl-3">
        <span className="w-2 h-2 rounded-full bg-emerald-400 inline-block" />
        <span className="text-[10px] text-emerald-400 font-sans font-semibold">GSD 30m</span>
      </div>
    </div>
  );
};
