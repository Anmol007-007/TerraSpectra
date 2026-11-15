import React from "react";

export interface LegendProps {
  hotspotDetected?: boolean;
  hotspotAcres?: number;
}

export const Legend: React.FC<LegendProps> = ({
  hotspotDetected = true,
  hotspotAcres = 5.2,
}) => {
  return (
    <div className="border-t border-[#3a506b]/50 pt-4" data-testid="disease-legend">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400">
          Disease Risk Scale
        </h2>
        {hotspotDetected && (
          <span className="text-[10px] font-bold text-red-400 bg-red-950/60 border border-red-800/80 px-1.5 py-0.5 rounded animate-pulse">
            {hotspotAcres} Ac Alert
          </span>
        )}
      </div>

      {/* Continuous gradient bar */}
      <div className="space-y-1 mb-3">
        <div className="h-2.5 w-full rounded-sm bg-gradient-to-r from-[#10b981] via-[#f59e0b] to-[#ef4444] border border-[#3a506b]/60" />
        <div className="flex justify-between text-[10px] text-slate-400 font-mono">
          <span>0.0 Healthy</span>
          <span>0.5 Warning</span>
          <span>1.0 Blight</span>
        </div>
      </div>

      {/* Discrete class categories */}
      <div className="space-y-1.5 text-xs text-slate-300">
        <div className="flex items-center space-x-2">
          <span className="w-3 h-3 rounded-sm bg-[#10b981] shrink-0" />
          <span>Healthy (Baseline Chlorophyll)</span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="w-3 h-3 rounded-sm bg-[#f59e0b] shrink-0" />
          <span>Pre-symptomatic Stress (21-Day Forecast)</span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="w-3 h-3 rounded-sm bg-[#ef4444] shrink-0" />
          <span>High Blight Risk (5-Acre Hotspot)</span>
        </div>
      </div>
    </div>
  );
};
