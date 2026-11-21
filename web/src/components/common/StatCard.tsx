import React from "react";

export interface StatCardProps {
  title: string;
  value: string | number;
  unit?: string;
  subtitle?: string;
  trend?: {
    value: string;
    isPositive?: boolean;
    isWarning?: boolean;
  };
  indicatorColor?: string;
  loading?: boolean;
  testId?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  unit,
  subtitle,
  trend,
  indicatorColor,
  loading = false,
  testId = "stat-card",
}) => {
  if (loading) {
    return (
      <div
        className="p-3 bg-[#1f2a4a]/70 rounded-lg border border-[#3a506b]/40 animate-pulse space-y-2"
        data-testid={`${testId}-skeleton`}
      >
        <div className="h-3 w-20 bg-slate-700/60 rounded" />
        <div className="h-6 w-28 bg-slate-700/80 rounded" />
        <div className="h-2 w-32 bg-slate-700/50 rounded" />
      </div>
    );
  }

  return (
    <div
      className="p-3 bg-[#1f2a4a]/80 hover:bg-[#1f2a4a] transition-colors rounded-lg border border-[#3a506b]/50 relative overflow-hidden"
      data-testid={testId}
    >
      {indicatorColor && (
        <div
          className="absolute top-0 left-0 bottom-0 w-1"
          style={{ backgroundColor: indicatorColor }}
        />
      )}
      <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
        <span className="font-medium tracking-wide uppercase text-[10px]">{title}</span>
        {trend && (
          <span
            className={`text-[10px] font-semibold px-1.5 py-0.5 rounded ${
              trend.isWarning
                ? "bg-red-500/20 text-red-400"
                : trend.isPositive
                ? "bg-emerald-500/20 text-emerald-400"
                : "bg-slate-700/50 text-slate-300"
            }`}
          >
            {trend.value}
          </span>
        )}
      </div>

      <div className="flex items-baseline space-x-1">
        <span className="text-xl font-bold text-white tracking-tight">{value}</span>
        {unit && <span className="text-xs text-slate-400 font-medium">{unit}</span>}
      </div>

      {subtitle && <p className="text-[11px] text-slate-400 mt-1">{subtitle}</p>}
    </div>
  );
};
