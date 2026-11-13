import { create } from "zustand";
import { DEFAULT_LAYER_VISIBILITY, type LayerVisibility } from "../layers/layerRegistry";

interface LayerState {
  visibility: LayerVisibility;
  heatmapOpacity: number;
  riskThreshold: number;
  toggleLayer: (layerName: keyof LayerVisibility) => void;
  setHeatmapOpacity: (val: number) => void;
  setRiskThreshold: (val: number) => void;
}

export const useLayerStore = create<LayerState>((set) => ({
  visibility: DEFAULT_LAYER_VISIBILITY,
  heatmapOpacity: 0.85,
  riskThreshold: 0.50,
  toggleLayer: (name) =>
    set((state) => ({
      visibility: {
        ...state.visibility,
        [name]: !state.visibility[name],
      },
    })),
  setHeatmapOpacity: (val) => set({ heatmapOpacity: val }),
  setRiskThreshold: (val) => set({ riskThreshold: val }),
}));
