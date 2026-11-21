import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
} from "recharts";
import { ResponsiveChartContainer } from "./ResponsiveChartContainer";
import { CHART_THEME } from "../../styles/chartTheme";
import type { StateAcreageItem } from "../../types/analytics";

export interface AcreageDistributionChartProps {
  data: StateAcreageItem[];
  height?: number;
}

export const AcreageDistributionChart: React.FC<AcreageDistributionChartProps> = ({
  data,
  height = 190,
}) => {
  if (!data || data.length === 0) {
    return (
      <div className="h-44 flex items-center justify-center text-xs text-slate-500">
        No acreage data available
      </div>
    );
  }

  return (
    <div className="w-full bg-[#1f2a4a]/40 p-3 rounded-lg border border-[#3a506b]/40">
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-xs font-semibold text-slate-300">Acreage Breakdown (Acres)</h4>
        <span className="text-[10px] text-slate-400">Total 1,000 ac</span>
      </div>

      <ResponsiveChartContainer height={height} minHeight={150}>
        <BarChart data={data} layout="vertical" margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
          <XAxis
            type="number"
            tick={{ fill: CHART_THEME.colors.textMuted, fontSize: 10 }}
            stroke={CHART_THEME.colors.border}
            unit=" ac"
          />
          <YAxis
            dataKey="label"
            type="category"
            tick={{ fill: CHART_THEME.colors.textMuted, fontSize: 10 }}
            stroke={CHART_THEME.colors.border}
            width={110}
          />
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const item = payload[0].payload as StateAcreageItem;
                return (
                  <div className="bg-[#0b132b] p-2 rounded border border-[#3a506b] shadow-lg text-xs">
                    <p className="font-semibold text-slate-200">{item.label}</p>
                    <p className="text-slate-300 font-mono mt-0.5">
                      Area: <span className="font-bold text-white">{item.acres}</span> acres
                    </p>
                    <p className="text-[#5bc0be] font-mono">
                      Share: <span className="font-bold">{item.percentage}%</span>
                    </p>
                  </div>
                );
              }
              return null;
            }}
          />
          <Bar dataKey="acres" radius={[0, 4, 4, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveChartContainer>
    </div>
  );
};
