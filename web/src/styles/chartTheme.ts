/**
 * Theme tokens and styling definitions for Recharts visualisations in TerraSpectra.
 */

export const CHART_THEME = {
  colors: {
    healthy: "#10b981",    // Emerald 500
    stressed: "#f59e0b",   // Amber 500
    diseased: "#ef4444",   // Red 500
    background: "#141d36",
    surface: "#1f2a4a",
    border: "#3a506b",
    textPrimary: "#f1f5f9",
    textMuted: "#94a3b8",
    gridLines: "#2a395c",
    tooltipBg: "#0b132b",
    cyanAccent: "#5bc0be",
  },
  typography: {
    fontFamily: "inherit",
    fontSize: 11,
  },
  animationDuration: 400,
} as const;
