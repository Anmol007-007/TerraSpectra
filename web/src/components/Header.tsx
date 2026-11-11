import React from "react";

interface HeaderProps {
  sceneId?: string;
  onRunPrediction?: () => void;
  isRunning?: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  sceneId = "farm_001",
  onRunPrediction,
  isRunning = false,
}) => {
  return (
    <header className="h-14 bg-[#1c2541] border-b border-[#3a506b] px-4 flex items-center justify-between z-10">
      <div className="flex items-center space-x-3">
        <span className="text-xl">🌿</span>
        <h1 className="font-bold text-lg text-slate-100 tracking-wide">
          TerraSpectra <span className="text-xs font-normal text-[#5bc0be] ml-1">Hyperspectral AI</span>
        </h1>
      </div>

      <div className="flex items-center space-x-4">
        <div className="text-xs text-slate-400">
          Scene: <span className="text-slate-200 font-mono">{sceneId}</span>
        </div>

        <button
          onClick={onRunPrediction}
          disabled={isRunning}
          className={`px-3 py-1.5 rounded text-xs font-semibold uppercase tracking-wider transition-colors ${
            isRunning
              ? "bg-slate-700 text-slate-400 cursor-not-allowed"
              : "bg-[#ef4444] hover:bg-red-600 text-white shadow-md shadow-red-950/40"
          }`}
        >
          {isRunning ? "Forecasting..." : "Run Forecast"}
        </button>
      </div>
    </header>
  );
};
