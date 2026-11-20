import React from "react";

export interface SkeletonProps {
  className?: string;
  count?: number;
}

export const Skeleton: React.FC<SkeletonProps> = ({ className = "h-4 w-full", count = 1 }) => {
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          data-testid="skeleton-pulse"
          className={`bg-slate-700/60 animate-pulse rounded ${className}`}
        />
      ))}
    </>
  );
};

export const CardSkeleton: React.FC = () => {
  return (
    <div className="bg-[#1c2541] p-4 rounded-xl border border-[#3a506b] space-y-3">
      <Skeleton className="h-3 w-1/3" />
      <Skeleton className="h-6 w-2/3" />
      <Skeleton className="h-3 w-1/2" />
    </div>
  );
};

export const MapLoadingSkeleton: React.FC = () => {
  return (
    <div
      data-testid="map-loading-skeleton"
      className="absolute inset-0 bg-[#0b132b]/80 backdrop-blur-sm z-20 flex flex-col items-center justify-center space-y-4"
    >
      <div className="w-12 h-12 border-4 border-[#5bc0be]/30 border-t-[#5bc0be] rounded-full animate-spin" />
      <div className="text-center space-y-1">
        <p className="text-sm font-semibold text-slate-200">Loading Hyperspectral Raster Cube...</p>
        <p className="text-xs text-slate-400 font-mono">Aligning 30m GSD grid to WGS84 coordinates</p>
      </div>
    </div>
  );
};
