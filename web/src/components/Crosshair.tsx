import React from "react";

interface CrosshairProps {
  visible?: boolean;
}

export const Crosshair: React.FC<CrosshairProps> = ({ visible = true }) => {
  if (!visible) return null;

  return (
    <div
      className="absolute inset-0 pointer-events-none flex items-center justify-center z-10"
      data-testid="gis-crosshair"
      aria-hidden="true"
    >
      <div className="relative flex items-center justify-center">
        {/* Reticle Circle: 15m radius indicator */}
        <div className="w-10 h-10 rounded-full border border-[#5bc0be]/60 animate-pulse" />

        {/* Inner target dot */}
        <div className="w-1.5 h-1.5 rounded-full bg-[#6fffe9] absolute" />

        {/* Horizontal Reticle Arms */}
        <div className="w-8 h-[1px] bg-[#5bc0be]/80 absolute -left-9" />
        <div className="w-8 h-[1px] bg-[#5bc0be]/80 absolute -right-9" />

        {/* Vertical Reticle Arms */}
        <div className="h-8 w-[1px] bg-[#5bc0be]/80 absolute -top-9" />
        <div className="h-8 w-[1px] bg-[#5bc0be]/80 absolute -bottom-9" />

        {/* Scale reference label */}
        <span className="absolute -bottom-6 text-[9px] font-mono text-[#5bc0be]/80 bg-[#0b132b]/80 px-1 rounded border border-[#3a506b]/40">
          30m GSD
        </span>
      </div>
    </div>
  );
};
