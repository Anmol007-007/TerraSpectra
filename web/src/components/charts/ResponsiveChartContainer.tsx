import React from "react";
import { ResponsiveContainer } from "recharts";

export interface ResponsiveChartContainerProps {
  height?: number | string;
  minHeight?: number;
  className?: string;
  children: React.ReactElement;
}

export const ResponsiveChartContainer: React.FC<ResponsiveChartContainerProps> = ({
  height = 200,
  minHeight = 160,
  className = "",
  children,
}) => {
  return (
    <div
      style={{ width: "100%", height, minHeight }}
      className={`relative w-full ${className}`}
      data-testid="responsive-chart-container"
    >
      <ResponsiveContainer width="100%" height="100%">
        {children}
      </ResponsiveContainer>
    </div>
  );
};
