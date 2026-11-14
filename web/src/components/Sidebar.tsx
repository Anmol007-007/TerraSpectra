import React from "react";
import { LayerPanel } from "./LayerPanel";

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-72 bg-[#141d36] border-r border-[#3a506b] p-4 flex flex-col space-y-6 text-sm overflow-y-auto">
      <div className="flex items-center justify-between border-b border-[#3a506b]/40 pb-2">
        <h2 className="text-xs font-bold uppercase tracking-wider text-slate-300">
          GIS Layers & Analysis
        </h2>
        <span className="text-[10px] text-[#5bc0be] bg-[#0b132b] px-2 py-0.5 rounded border border-[#3a506b]">
          v0.1.0
        </span>
      </div>

      <LayerPanel />

      <div className="border-t border-[#3a506b]/50 pt-4">
        <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
          Legend
        </h2>
        <div className="space-y-1.5 text-xs text-slate-300">
          <div className="flex items-center space-x-2">
            <span className="w-3 h-3 rounded-sm bg-[#10b981]" />
            <span>Healthy (Normal)</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="w-3 h-3 rounded-sm bg-[#f59e0b]" />
            <span>Pre-symptomatic Stress (21-Day)</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="w-3 h-3 rounded-sm bg-[#ef4444]" />
            <span>Fungal Blight Risk (5-Acre Zone)</span>
          </div>
        </div>
      </div>
    </aside>
  );
};
