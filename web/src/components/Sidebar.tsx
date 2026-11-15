import React from "react";
import { LayerPanel } from "./LayerPanel";
import { Legend } from "./Legend";

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

      <Legend />
    </aside>
  );
};
