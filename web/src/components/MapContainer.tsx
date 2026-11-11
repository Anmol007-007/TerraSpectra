import React from "react";

export const MapContainer: React.FC = () => {
  return (
    <div className="w-full h-full bg-[#0a1128] flex flex-col items-center justify-center p-6 text-center select-none">
      <div className="p-4 rounded-xl bg-[#1c2541]/80 border border-[#3a506b] max-w-md shadow-2xl backdrop-blur">
        <div className="text-3xl mb-2">🗺️</div>
        <h3 className="font-semibold text-slate-200 mb-1">Deck.gl 3D GIS Viewport</h3>
        <p className="text-xs text-slate-400 mb-4">
          Hyperspectral 200+ band risk overlay (EPSG:4326 / UTM 43N)
        </p>
        <div className="inline-flex items-center text-[11px] text-[#5bc0be] bg-[#0b132b] px-3 py-1 rounded-full border border-[#3a506b]">
          Farm target: 1,000 acres · 30m GSD · 21-day forecast
        </div>
      </div>
    </div>
  );
};
