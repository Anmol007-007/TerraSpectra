import React, { useEffect } from "react";
import { ToggleSwitch } from "./ToggleSwitch";
import { OpacitySlider } from "./OpacitySlider";
import { useLayerStore } from "../store/layerStore";

interface LayerPanelProps {
  onResetView?: () => void;
  onPitchChange?: (pitch: number) => void;
  pitch?: number;
}

export const LayerPanel: React.FC<LayerPanelProps> = ({
  onResetView,
  onPitchChange,
  pitch = 45,
}) => {
  const {
    visibility,
    heatmapOpacity,
    riskThreshold,
    terrain3d,
    toggleLayer,
    toggleTerrain3d,
    setHeatmapOpacity,
    setRiskThreshold,
  } = useLayerStore();

  // Keyboard shortcuts (F: farm boundary, P: parcels, H: heatmap, Z: zones, T: 3D terrain)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }
      switch (e.key.toLowerCase()) {
        case "f":
          toggleLayer("farmBoundary");
          break;
        case "p":
          toggleLayer("parcels");
          break;
        case "h":
          toggleLayer("heatmap");
          break;
        case "z":
          toggleLayer("zones");
          break;
        case "t":
          toggleTerrain3d();
          break;
        default:
          break;
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [toggleLayer, toggleTerrain3d]);

  return (
    <div className="space-y-5 text-sm" data-testid="layer-panel">
      {/* 1. Geospatial Farm Layers */}
      <div>
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
          GIS Layers (Keys F, P, H, Z)
        </h3>
        <div className="space-y-1 bg-[#0b132b]/60 p-2.5 rounded-lg border border-[#3a506b]/40">
          <ToggleSwitch
            label="1,000-Acre Farm Boundary"
            checked={visibility.farmBoundary}
            onChange={() => toggleLayer("farmBoundary")}
            badge="Boundary"
          />
          <ToggleSwitch
            label="Agricultural Parcels"
            checked={visibility.parcels}
            onChange={() => toggleLayer("parcels")}
            badge="4 Fields"
            badgeColor="bg-slate-300"
          />
          <ToggleSwitch
            label="Disease Risk Heatmap"
            checked={visibility.heatmap}
            onChange={() => toggleLayer("heatmap")}
            badge="AI Grid"
            badgeColor="bg-[#ef4444] text-white"
          />
          <ToggleSwitch
            label="5-Acre Blight Hotspot Zone"
            checked={visibility.zones}
            onChange={() => toggleLayer("zones")}
            badge="Forecast"
            badgeColor="bg-[#f59e0b]"
          />
        </div>
      </div>

      {/* 2. Visual Layer Controls */}
      <div>
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
          Display Controls
        </h3>
        <div className="bg-[#0b132b]/60 p-2.5 rounded-lg border border-[#3a506b]/40 space-y-1">
          <OpacitySlider
            label="Heatmap Opacity"
            value={heatmapOpacity}
            onChange={setHeatmapOpacity}
          />
          <OpacitySlider
            label="Risk Probability Cutoff"
            value={riskThreshold}
            onChange={setRiskThreshold}
            accentColor="accent-[#ef4444]"
          />
        </div>
      </div>

      {/* 3. 3D Terrain & Camera Pitch Controls */}
      <div>
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
          3D Perspective (Key T)
        </h3>
        <div className="bg-[#0b132b]/60 p-2.5 rounded-lg border border-[#3a506b]/40 space-y-3">
          <ToggleSwitch
            label="3D Topographic Terrain"
            checked={terrain3d}
            onChange={toggleTerrain3d}
            badge="DEM"
            badgeColor="bg-[#6fffe9]"
          />

          <div>
            <div className="flex justify-between items-center mb-1 text-xs">
              <span className="text-slate-300">Camera Pitch (3D Tilt)</span>
              <span className="text-slate-400 font-mono text-[11px]">{Math.round(pitch)}°</span>
            </div>
            <input
              type="range"
              min={0}
              max={60}
              step={5}
              value={pitch}
              onChange={(e) => onPitchChange?.(parseFloat(e.target.value))}
              className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-[#5bc0be]"
            />
          </div>

          {onResetView && (
            <button
              onClick={onResetView}
              className="w-full py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded border border-[#3a506b] transition-colors"
            >
              Reset 3D Camera View
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
