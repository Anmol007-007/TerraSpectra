import React from "react";
import { useLayerStore } from "../store/layerStore";

export const PixelInspector: React.FC = () => {
  const { hoveredCell, selectedCell, setSelectedCell } = useLayerStore();
  const cell = selectedCell || hoveredCell;

  if (!cell) {
    return (
      <div
        className="bg-[#141d36]/90 backdrop-blur border border-[#3a506b]/60 rounded-lg p-3 text-xs text-slate-400"
        data-testid="pixel-inspector"
      >
        <span className="font-semibold text-slate-300">Pixel Inspector:</span> Hover or click a 30m
        grid cell to inspect spectral health metrics.
      </div>
    );
  }

  const stateLabels = ["Healthy", "Pre-Symptomatic (21d)", "Visibly Diseased"];
  const stateBadgeColors = [
    "bg-[#10b981] text-[#0b132b]",
    "bg-[#f59e0b] text-[#0b132b]",
    "bg-[#ef4444] text-white",
  ];

  return (
    <div
      className="bg-[#141d36]/95 backdrop-blur border border-[#5bc0be]/50 rounded-lg p-3.5 text-xs shadow-xl space-y-2.5 max-w-xs"
      data-testid="pixel-inspector"
    >
      <div className="flex items-center justify-between border-b border-[#3a506b]/50 pb-1.5">
        <span className="font-bold text-slate-200">
          Pixel [{cell.r}, {cell.c}]
        </span>
        <span
          className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${stateBadgeColors[cell.state]}`}
        >
          {stateLabels[cell.state]}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[11px]">
        <div>
          <span className="text-slate-400 block">Disease Risk:</span>
          <span className="font-mono font-bold text-slate-100">
            {(cell.risk * 100).toFixed(1)}%
          </span>
        </div>
        <div>
          <span className="text-slate-400 block">Lesion Severity:</span>
          <span className="font-mono font-bold text-slate-100">
            {(cell.severity * 100).toFixed(1)}%
          </span>
        </div>
        <div>
          <span className="text-slate-400 block">Uncertainty:</span>
          <span className="font-mono font-bold text-slate-100">
            ±{(cell.uncertainty * 100).toFixed(1)}%
          </span>
        </div>
        <div>
          <span className="text-slate-400 block">Forecast Horizon:</span>
          <span className="font-mono font-bold text-slate-100">
            {cell.days_to_symptoms !== undefined ? `${cell.days_to_symptoms} days` : "N/A"}
          </span>
        </div>
      </div>

      <div className="text-[10px] text-slate-400 font-mono">
        Lon: {cell.lon.toFixed(5)}, Lat: {cell.lat.toFixed(5)}
      </div>

      {selectedCell && (
        <button
          onClick={() => setSelectedCell(null)}
          className="w-full mt-1 py-1 text-[10px] text-slate-400 hover:text-white bg-slate-800 rounded border border-[#3a506b]/40"
        >
          Clear Selection
        </button>
      )}
    </div>
  );
};
