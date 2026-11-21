import React from "react";
import { AnalyticsPanel } from "../panels/AnalyticsPanel";
import { useUiStore } from "../../store/uiStore";

export const RightSidebar: React.FC = () => {
  const { analyticsOpen, toggleAnalytics } = useUiStore();

  return (
    <aside
      className={`relative transition-all duration-300 ease-in-out shrink-0 border-l border-[#3a506b] bg-[#141d36] flex flex-col ${
        analyticsOpen ? "w-84" : "w-10"
      }`}
      style={{ width: analyticsOpen ? "22rem" : "2.5rem" }}
      data-testid="right-sidebar"
    >
      {/* Collapse/Expand Toggle Button */}
      <button
        onClick={toggleAnalytics}
        className="absolute -left-3 top-4 z-20 w-6 h-6 rounded-full bg-[#1f2a4a] border border-[#3a506b] text-slate-300 hover:text-white flex items-center justify-center text-xs shadow-md transition-transform hover:scale-110"
        title={analyticsOpen ? "Collapse Analytics" : "Expand Analytics"}
        aria-label={analyticsOpen ? "Collapse Analytics" : "Expand Analytics"}
        data-testid="toggle-analytics-btn"
      >
        {analyticsOpen ? "›" : "‹"}
      </button>

      {analyticsOpen ? (
        <AnalyticsPanel />
      ) : (
        <div
          className="h-full flex flex-col items-center py-6 cursor-pointer hover:bg-[#1f2a4a]/40 transition-colors"
          onClick={toggleAnalytics}
          title="Open Analytics"
        >
          <span className="text-[11px] font-bold uppercase tracking-widest text-slate-400 [writing-mode:vertical-lr] rotate-180">
            Analytics & KPIs
          </span>
        </div>
      )}
    </aside>
  );
};
