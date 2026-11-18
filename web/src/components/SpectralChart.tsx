import React from "react";
import type { CropState } from "../types/heatmap";

export interface SpectralChartProps {
  state?: CropState;
  customBands?: number[];
  width?: number;
  height?: number;
}

export const SpectralChart: React.FC<SpectralChartProps> = ({
  state = 0,
  customBands,
  width = 240,
  height = 90,
}) => {
  let reflectance: number[];
  let lineColor: string;

  if (customBands && customBands.length > 0) {
    reflectance = customBands.slice(0, 20);
    lineColor = "#5bc0be";
  } else if (state === 2) {
    // Diseased necrosis: low NIR, loss of chlorophyll red edge
    reflectance = [
      0.15, 0.18, 0.22, 0.24, 0.26, 0.28, 0.32, 0.35, 0.36, 0.36, 0.32, 0.30, 0.28, 0.25, 0.18,
      0.22, 0.16, 0.18, 0.14, 0.12,
    ];
    lineColor = "#ef4444";
  } else if (state === 1) {
    // Pre-symptomatic (~21d forecast): subtle red-edge blue shift and slight NIR drop
    reflectance = [
      0.08, 0.10, 0.14, 0.11, 0.09, 0.18, 0.40, 0.54, 0.58, 0.58, 0.48, 0.50, 0.46, 0.42, 0.22,
      0.32, 0.20, 0.25, 0.16, 0.14,
    ];
    lineColor = "#f59e0b";
  } else {
    // Healthy canopy: low visible, sharp red edge, high NIR reflectance
    reflectance = [
      0.06, 0.08, 0.15, 0.09, 0.07, 0.15, 0.46, 0.65, 0.70, 0.70, 0.58, 0.60, 0.54, 0.50, 0.25,
      0.38, 0.22, 0.28, 0.18, 0.15,
    ];
    lineColor = "#10b981";
  }

  const padding = 10;
  const innerW = width - padding * 2;
  const innerH = height - padding * 2;

  const maxVal = 0.8;
  const minVal = 0.0;

  const points = reflectance
    .map((val, idx) => {
      const x = padding + (idx / (reflectance.length - 1)) * innerW;
      const y = height - padding - ((val - minVal) / (maxVal - minVal)) * innerH;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");

  return (
    <div className="space-y-1" data-testid="spectral-chart">
      <div className="flex justify-between items-center text-[10px] text-slate-400 font-mono">
        <span>Reflectance Curve (400 - 2400nm)</span>
        <span style={{ color: lineColor }} className="font-bold">
          {state === 2 ? "Diseased" : state === 1 ? "Pre-Symptomatic" : "Healthy"}
        </span>
      </div>
      <div className="bg-[#0b132b]/80 border border-[#3a506b]/40 rounded p-1">
        <svg width={width} height={height} className="overflow-visible">
          {/* Reference grid line */}
          <line
            x1={padding}
            y1={height / 2}
            x2={width - padding}
            y2={height / 2}
            stroke="#3a506b"
            strokeDasharray="2 2"
            strokeWidth="0.5"
          />
          {/* Reflectance Polyline */}
          <polyline fill="none" stroke={lineColor} strokeWidth="2" points={points} />
        </svg>
      </div>
    </div>
  );
};
