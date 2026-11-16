import { create } from "zustand";
import { persist } from "zustand/middleware";
import { DEFAULT_LAYER_VISIBILITY, type LayerVisibility } from "../layers/layerRegistry";
import type { PredictionCell } from "../types/heatmap";

interface LayerState {
  visibility: LayerVisibility;
  heatmapOpacity: number;
  riskThreshold: number;
  terrain3d: boolean;
  pixelGridMode: boolean;
  hoveredCell: PredictionCell | null;
  selectedCell: PredictionCell | null;
  toggleLayer: (layerName: keyof LayerVisibility) => void;
  toggleTerrain3d: () => void;
  setHeatmapOpacity: (val: number) => void;
  setRiskThreshold: (val: number) => void;
  setPixelGridMode: (val: boolean) => void;
  setHoveredCell: (cell: PredictionCell | null) => void;
  setSelectedCell: (cell: PredictionCell | null) => void;
  resetAllLayers: () => void;
}

export const useLayerStore = create<LayerState>()(
  persist(
    (set) => ({
      visibility: DEFAULT_LAYER_VISIBILITY,
      heatmapOpacity: 0.85,
      riskThreshold: 0.50,
      terrain3d: true,
      pixelGridMode: false,
      hoveredCell: null,
      selectedCell: null,
      toggleLayer: (name) =>
        set((state) => ({
          visibility: {
            ...state.visibility,
            [name]: !state.visibility[name],
          },
        })),
      toggleTerrain3d: () =>
        set((state) => ({
          terrain3d: !state.terrain3d,
        })),
      setHeatmapOpacity: (val) => set({ heatmapOpacity: val }),
      setRiskThreshold: (val) => set({ riskThreshold: val }),
      setPixelGridMode: (val) => set({ pixelGridMode: val }),
      setHoveredCell: (cell) => set({ hoveredCell: cell }),
      setSelectedCell: (cell) => set({ selectedCell: cell }),
      resetAllLayers: () =>
        set({
          visibility: DEFAULT_LAYER_VISIBILITY,
          heatmapOpacity: 0.85,
          riskThreshold: 0.50,
          terrain3d: true,
          pixelGridMode: false,
          hoveredCell: null,
          selectedCell: null,
        }),
    }),
    {
      name: "terraspectra-layer-storage",
    }
  )
);
