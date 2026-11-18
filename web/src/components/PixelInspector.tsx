import React from "react";
import { useLayerStore } from "../store/layerStore";
import { SpectralChart } from "./SpectralChart";
import { Tooltip } from "./Tooltip";

export interface PixelInspectorProps {
  onZoomToPixel?: (lon: number, lat: number) => void;
}

export const PixelInspector: React.FC<PixelInspectorProps> = ({ onZoomToPixel }) => {
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

  const stateExplanations = [
    "Healthy canopy: Normal chlorophyll reflectance with sharp red edge and high NIR absorption plateau.",
    "Pre-symptomatic stress: Subtle ~21-day incubation signature detected via red-edge shift before visible symptoms.",
    "Visibly diseased: Severe chlorophyll loss, cellular breakdown, and necrotic lesion formation.",
  ];

  return (
    <div
      className="bg-[#141d36]/95 backdrop-blur border border-[#5bc0be]/50 rounded-lg p-3.5 text-xs shadow-xl space-y-3 max-w-xs"
      data-testid="pixel-inspector"
    >
      <div className="flex items-center justify-between border-b border-[#3a506b]/50 pb-1.5">
        <span className="font-bold text-slate-200">
          Pixel [{cell.r}, {cell.c}]
        </span>
        <Tooltip content={stateExplanations[cell.state]}>
          <span
            className={`text-[10px] font-bold px-2 py-0.5 rounded-full cursor-help ${stateBadgeColors[cell.state]}`}
          >
            {stateLabels[cell.state]}
          </span>
        </Tooltip>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[11px]">
        <div>
          <Tooltip content="Probability that this 30m cell is infected by fungal blight (0% = healthy, 100% = infected).">
            <span className="text-slate-400 block cursor-help border-b border-dotted border-slate-600">
              Disease Risk:
            </span>
          </Tooltip>
          <span className="font-mono font-bold text-slate-100">
            {(cell.risk * 100).toFixed(1)}%
          </span>
        </div>
        <div>
          <Tooltip content="Estimated severity and cellular damage fraction inside the 30m pixel footprint.">
            <span className="text-slate-400 block cursor-help border-b border-dotted border-slate-600">
              Lesion Severity:
            </span>
          </Tooltip>
          <span className="font-mono font-bold text-slate-100">
            {(cell.severity * 100).toFixed(1)}%
          </span>
        </div>
        <div>
          <Tooltip content="Epistemic and aleatoric predictive uncertainty from Monte Carlo dropout sampling.">
            <span className="text-slate-400 block cursor-help border-b border-dotted border-slate-600">
              Uncertainty:
            </span>
          </Tooltip>
          <span className="font-mono font-bold text-slate-100">
            ±{(cell.uncertainty * 100).toFixed(1)}%
          </span>
        </div>
        <div>
          <Tooltip content="Forecast window indicating days remaining until visual symptoms manifest on field.">
            <span className="text-slate-400 block cursor-help border-b border-dotted border-slate-600">
              Forecast Horizon:
            </span>
          </Tooltip>
          <span className="font-mono font-bold text-slate-100">
            {cell.days_to_symptoms !== undefined ? `${cell.days_to_symptoms} days` : "N/A"}
          </span>
        </div>
      </div>

      {/* Spectral Signature Mini-Chart */}
      <div className="pt-1 border-t border-[#3a506b]/40">
        <SpectralChart state={cell.state} width={220} height={70} />
      </div>

      <div className="text-[10px] text-slate-400 font-mono">
        Lon: {cell.lon.toFixed(5)}, Lat: {cell.lat.toFixed(5)}
      </div>

      <div className="flex space-x-2 pt-1">
        {onZoomToPixel && (
          <button
            onClick={() => onZoomToPixel(cell.lon, cell.lat)}
            className="flex-1 py-1 text-[10px] text-[#5bc0be] hover:text-white bg-[#0b132b] hover:bg-slate-800 rounded border border-[#5bc0be]/40 font-semibold"
          >
            🎯 Zoom to Pixel
          </button>
        )}

        {selectedCell && (
          <button
            onClick={() => setSelectedCell(null)}
            className="flex-1 py-1 text-[10px] text-slate-400 hover:text-white bg-slate-800 rounded border border-[#3a506b]/40"
          >
            Clear
          </button>
        )}
      </div>
    </div>
  );
};
