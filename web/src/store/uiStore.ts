import { create } from "zustand";

interface UiState {
  theme: "dark" | "light";
  heatmapOpacity: number;
  riskThreshold: number;
  selectedZoneId: string | null;
  sidebarOpen: boolean;
  setHeatmapOpacity: (opacity: number) => void;
  setRiskThreshold: (threshold: number) => void;
  setSelectedZoneId: (id: string | null) => void;
  toggleSidebar: () => void;
}

export const useUiStore = create<UiState>((set) => ({
  theme: "dark",
  heatmapOpacity: 0.85,
  riskThreshold: 0.5,
  selectedZoneId: null,
  sidebarOpen: true,
  setHeatmapOpacity: (opacity) => set({ heatmapOpacity: opacity }),
  setRiskThreshold: (threshold) => set({ riskThreshold: threshold }),
  setSelectedZoneId: (id) => set({ selectedZoneId: id }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
}));
