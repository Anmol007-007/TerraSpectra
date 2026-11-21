import React from "react";

export interface TabsProps {
  tabs: Array<{ id: string; label: string; count?: number }>;
  activeTab: string;
  onChange: (id: string) => void;
}

export const Tabs: React.FC<TabsProps> = ({ tabs, activeTab, onChange }) => {
  return (
    <div className="flex border-b border-[#3a506b]/60 space-x-1" role="tablist">
      {tabs.map((tab) => {
        const isActive = tab.id === activeTab;
        return (
          <button
            key={tab.id}
            role="tab"
            aria-selected={isActive}
            onClick={() => onChange(tab.id)}
            className={`px-3 py-2 text-xs font-semibold tracking-wide border-b-2 transition-all flex items-center space-x-1.5 ${
              isActive
                ? "border-[#5bc0be] text-[#5bc0be] bg-[#1f2a4a]/40"
                : "border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-500"
            }`}
          >
            <span>{tab.label}</span>
            {tab.count !== undefined && (
              <span
                className={`text-[10px] px-1.5 py-0.2 rounded-full ${
                  isActive ? "bg-[#5bc0be]/20 text-[#5bc0be]" : "bg-slate-800 text-slate-400"
                }`}
              >
                {tab.count}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
};
