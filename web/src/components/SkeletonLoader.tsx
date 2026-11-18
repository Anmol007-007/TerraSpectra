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
