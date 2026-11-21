import { create } from "zustand";

export interface ToastMessage {
  id: string;
  type: "info" | "success" | "warning" | "error";
  message: string;
}

interface UiState {
  theme: "dark" | "light";
  heatmapOpacity: number;
  riskThreshold: number;
  selectedZoneId: string | null;
  sidebarOpen: boolean;
  analyticsOpen: boolean;
  toasts: ToastMessage[];
  setHeatmapOpacity: (opacity: number) => void;
  setRiskThreshold: (threshold: number) => void;
  setSelectedZoneId: (id: string | null) => void;
  toggleSidebar: () => void;
  toggleAnalytics: () => void;
  setAnalyticsOpen: (open: boolean) => void;
  addToast: (message: string, type?: ToastMessage["type"]) => void;
  removeToast: (id: string) => void;
}

export const useUiStore = create<UiState>((set) => ({
  theme: "dark",
  heatmapOpacity: 0.85,
  riskThreshold: 0.5,
  selectedZoneId: null,
  sidebarOpen: true,
  analyticsOpen: true,
  toasts: [],
  setHeatmapOpacity: (opacity) => set({ heatmapOpacity: opacity }),
  setRiskThreshold: (threshold) => set({ riskThreshold: threshold }),
  setSelectedZoneId: (id) => set({ selectedZoneId: id }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  toggleAnalytics: () => set((state) => ({ analyticsOpen: !state.analyticsOpen })),
  setAnalyticsOpen: (open) => set({ analyticsOpen: open }),
  addToast: (message, type = "info") => {
    const id = Math.random().toString(36).substring(2, 9);
    set((state) => ({
      toasts: [...state.toasts, { id, message, type }],
    }));
    setTimeout(() => {
      set((state) => ({
        toasts: state.toasts.filter((t) => t.id !== id),
      }));
    }, 4000);
  },
  removeToast: (id) =>
    set((state) => ({
      toasts: state.toasts.filter((t) => t.id !== id),
    })),
}));
