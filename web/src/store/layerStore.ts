import { create } from "zustand";
import { persist } from "zustand/middleware";
import { DEFAULT_LAYER_VISIBILITY, type LayerVisibility } from "../layers/layerRegistry";

interface LayerState {
  visibility: LayerVisibility;
  heatmapOpacity: number;
  riskThreshold: number;
  terrain3d: boolean;
  toggleLayer: (layerName: keyof LayerVisibility) => void;
  toggleTerrain3d: () => void;
  setHeatmapOpacity: (val: number) => void;
  setRiskThreshold: (val: number) => void;
  resetAllLayers: () => void;
}

export const useLayerStore = create<LayerState>()(
  persist(
    (set) => ({
      visibility: DEFAULT_LAYER_VISIBILITY,
      heatmapOpacity: 0.85,
      riskThreshold: 0.50,
      terrain3d: true,
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
      resetAllLayers: () =>
        set({
          visibility: DEFAULT_LAYER_VISIBILITY,
          heatmapOpacity: 0.85,
          riskThreshold: 0.50,
          terrain3d: true,
        }),
    }),
    {
      name: "terraspectra-layer-storage",
    }
  )
);
