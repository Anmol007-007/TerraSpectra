import React, { useState } from "react";
import { useLayerStore } from "../store/layerStore";
import { GSD_METRES } from "../utils/constants";
import mockPredictionData from "../api/mocks/farm_001_result.json";
import type { FarmPredictionResult, PredictionCell } from "../types/heatmap";
import { MapContainer } from "./MapContainer";

const MOCK_RESULT = mockPredictionData as unknown as FarmPredictionResult;

export const PixelGridDemo: React.FC = () => {
  const {
    pixelGridMode,
    setPixelGridMode,
    riskThreshold,
    setRiskThreshold,
    heatmapOpacity,
    setHeatmapOpacity,
    hoveredCell,
    selectedCell,
  } = useLayerStore();

  const [activeTab, setActiveTab] = useState<"viewport" | "matrix">("viewport");
  const cells: PredictionCell[] = MOCK_RESULT.cells;

  const healthyCount = cells.filter((c: PredictionCell) => c.state === 0).length;
  const preSymptomaticCount = cells.filter((c: PredictionCell) => c.state === 1).length;
  const highRiskCount = cells.filter((c: PredictionCell) => c.state === 2).length;

  return (
    <div
      className="flex flex-col h-full w-full bg-[#0b132b] text-slate-100 overflow-hidden"
      data-testid="pixel-grid-demo"
    >
      {/* Top Demo Bar */}
      <div className="bg-[#1c2541] border-b border-[#3a506b] px-6 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <span className="p-2 bg-[#5bc0be]/20 rounded-lg text-lg">🛰️</span>
          <div>
            <h2 className="font-bold text-sm text-slate-100 uppercase tracking-wider">
              30m GSD Hyperspectral Pixel Grid Demo
            </h2>
            <p className="text-xs text-slate-400">
              Interactive Deck.gl GridCellLayer • 30m Ground Sampling Distance (GSD)
            </p>
          </div>
        </div>

        {/* Tab & Controls Switcher */}
        <div className="flex items-center space-x-4">
          <div className="flex bg-[#0b132b] p-1 rounded-lg border border-[#3a506b]/50 text-xs">
            <button
              onClick={() => setActiveTab("viewport")}
              className={`px-3 py-1 rounded transition-colors ${
                activeTab === "viewport"
                  ? "bg-[#5bc0be] text-[#0b132b] font-bold"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Interactive 3D Map
            </button>
            <button
              onClick={() => setActiveTab("matrix")}
              className={`px-3 py-1 rounded transition-colors ${
                activeTab === "matrix"
                  ? "bg-[#5bc0be] text-[#0b132b] font-bold"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Cell Matrix Stats
            </button>
          </div>

          <button
            onClick={() => setPixelGridMode(!pixelGridMode)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
              pixelGridMode
                ? "bg-[#ef4444]/20 border-[#ef4444] text-[#ef4444]"
                : "bg-slate-800 border-slate-600 text-slate-300"
            }`}
          >
            {pixelGridMode ? "Grid Mode: Active (30m Cells)" : "Grid Mode: Inactive"}
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      {activeTab === "viewport" ? (
        <div className="relative flex-1 w-full h-full">
          <MapContainer />

          {/* Floating Grid Control HUD */}
          <div className="absolute top-4 left-4 z-10 bg-[#1c2541]/90 backdrop-blur-md p-4 rounded-xl border border-[#3a506b] shadow-2xl w-80 space-y-3">
            <div className="flex justify-between items-center border-b border-[#3a506b]/40 pb-2">
              <span className="text-xs font-bold uppercase text-[#5bc0be] tracking-wider">
                Grid Specifications
              </span>
              <span
                data-testid="gsd-badge"
                className="text-[10px] font-mono bg-slate-800 px-2 py-0.5 rounded text-slate-300"
              >
                {GSD_METRES}m GSD
              </span>
            </div>

            <div className="text-xs space-y-1.5 text-slate-300">
              <div className="flex justify-between">
                <span>Raster Resolution:</span>
                <span className="font-mono text-slate-200">
                  {MOCK_RESULT.grid_shape[0]} × {MOCK_RESULT.grid_shape[1]} px
                </span>
              </div>
              <div className="flex justify-between">
                <span>Farm Area Coverage:</span>
                <span className="font-mono text-slate-200">1,000 Acres</span>
              </div>
              <div className="flex justify-between">
                <span>Blight Hotspot Zone:</span>
                <span className="font-mono text-red-400 font-bold">5 Acres (22-23 cells)</span>
              </div>
            </div>

            {/* Threshold Sliders */}
            <div className="pt-2 border-t border-[#3a506b]/40 space-y-2">
              <div>
                <div className="flex justify-between text-[11px] text-slate-400 mb-1">
                  <span>Risk Cutoff Threshold</span>
                  <span className="font-mono text-red-400">{Math.round(riskThreshold * 100)}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={riskThreshold}
                  onChange={(e) => setRiskThreshold(parseFloat(e.target.value))}
                  className="w-full h-1 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-[#ef4444]"
                />
              </div>

              <div>
                <div className="flex justify-between text-[11px] text-slate-400 mb-1">
                  <span>Layer Opacity</span>
                  <span className="font-mono text-slate-200">{Math.round(heatmapOpacity * 100)}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={heatmapOpacity}
                  onChange={(e) => setHeatmapOpacity(parseFloat(e.target.value))}
                  className="w-full h-1 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-[#5bc0be]"
                />
              </div>
            </div>

            {/* Quick Status Pill */}
            <div className="p-2 bg-[#0b132b]/80 rounded border border-[#3a506b]/40 text-[11px] text-slate-300">
              {hoveredCell || selectedCell ? (
                <div className="text-emerald-400 font-mono">
                  Cell Selected: Row {(hoveredCell || selectedCell)?.r}, Col {(hoveredCell || selectedCell)?.c}
                </div>
              ) : (
                <div className="text-slate-400 italic">
                  Hover or click any 30m cell on the map to inspect spectral telemetry.
                </div>
              )}
            </div>
          </div>
        </div>
      ) : (
        /* Matrix Statistics View */
        <div className="flex-1 p-6 overflow-y-auto space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-[#1c2541] p-4 rounded-xl border border-[#3a506b]">
              <div className="text-xs text-slate-400 uppercase">Healthy Canopy</div>
              <div className="text-2xl font-bold text-emerald-400 mt-1">{healthyCount} Cells</div>
              <div className="text-xs text-slate-500 mt-1">Normal reflectance across 224 bands</div>
            </div>
            <div className="bg-[#1c2541] p-4 rounded-xl border border-[#3a506b]">
              <div className="text-xs text-slate-400 uppercase">Pre-Symptomatic Stress</div>
              <div className="text-2xl font-bold text-amber-400 mt-1">{preSymptomaticCount} Cells</div>
              <div className="text-xs text-slate-500 mt-1">~21-day incubation red-edge shifts</div>
            </div>
            <div className="bg-[#1c2541] p-4 rounded-xl border border-[#3a506b]">
              <div className="text-xs text-slate-400 uppercase">High Risk Blight Hotspot</div>
              <div className="text-2xl font-bold text-red-400 mt-1">{highRiskCount} Cells</div>
              <div className="text-xs text-slate-500 mt-1">Targeted 5-acre fungal infection zone</div>
            </div>
          </div>

          <div className="bg-[#1c2541] p-5 rounded-xl border border-[#3a506b] space-y-3">
            <h3 className="font-semibold text-sm text-slate-200">
              Active Grid Telemetry Sample (First 10 Cells)
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left text-slate-300">
                <thead className="bg-[#0b132b] text-slate-400 uppercase font-mono text-[10px]">
                  <tr>
                    <th className="py-2 px-3">Row / Col</th>
                    <th className="py-2 px-3">Coordinates (Lng, Lat)</th>
                    <th className="py-2 px-3">Risk Probability</th>
                    <th className="py-2 px-3">Uncertainty</th>
                    <th className="py-2 px-3">State</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#3a506b]/40">
                  {cells.slice(0, 10).map((cell: PredictionCell, idx: number) => (
                    <tr key={idx} className="hover:bg-slate-800/50">
                      <td className="py-2 px-3 font-mono">
                        R{cell.r} : C{cell.c}
                      </td>
                      <td className="py-2 px-3 font-mono">
                        {cell.lon.toFixed(5)}, {cell.lat.toFixed(5)}
                      </td>
                      <td className="py-2 px-3 font-bold font-mono">
                        <span
                          className={
                            cell.risk >= 0.7
                              ? "text-red-400"
                              : cell.risk >= 0.35
                              ? "text-amber-400"
                              : "text-emerald-400"
                          }
                        >
                          {(cell.risk * 100).toFixed(1)}%
                        </span>
                      </td>
                      <td className="py-2 px-3 font-mono text-slate-400">
                        ±{(cell.uncertainty * 100).toFixed(1)}%
                      </td>
                      <td className="py-2 px-3">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase ${
                            cell.state === 2
                              ? "bg-red-900/60 text-red-300 border border-red-700/60"
                              : cell.state === 1
                              ? "bg-amber-900/60 text-amber-300 border border-amber-700/60"
                              : "bg-emerald-900/60 text-emerald-300 border border-emerald-700/60"
                          }`}
                        >
                          {cell.state === 2 ? "diseased" : cell.state === 1 ? "pre_symptomatic" : "healthy"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
