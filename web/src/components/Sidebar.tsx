import React from "react";

interface SidebarProps {
  opacity?: number;
  onOpacityChange?: (val: number) => void;
  threshold?: number;
  onThresholdChange?: (val: number) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  opacity = 0.8,
  onOpacityChange,
  threshold = 0.5,
  onThresholdChange,
}) => {
  return (
    <aside className="w-64 bg-[#141d36] border-r border-[#3a506b] p-4 flex flex-col space-y-6 text-sm">
      <div>
        <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">
          Layer Controls
        </h2>
        <div className="space-y-4">
          <div>
            <label className="text-xs text-slate-300 block mb-1">Heatmap Opacity</label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={opacity}
              onChange={(e) => onOpacityChange?.(parseFloat(e.target.value))}
              className="w-full accent-[#5bc0be]"
            />
          </div>

          <div>
            <label className="text-xs text-slate-300 block mb-1">
              Risk Threshold ({threshold.toFixed(2)})
            </label>
            <input
              type="range"
              min="0.1"
              max="0.9"
              step="0.05"
              value={threshold}
              onChange={(e) => onThresholdChange?.(parseFloat(e.target.value))}
              className="w-full accent-[#ef4444]"
            />
          </div>
        </div>
      </div>

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
            <span>Pre-symptomatic Stress</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="w-3 h-3 rounded-sm bg-[#ef4444]" />
            <span>Fungal Blight Risk (5-acre)</span>
          </div>
        </div>
      </div>
    </aside>
  );
};
