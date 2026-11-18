import React, { useState } from "react";

export interface TooltipProps {
  content: React.ReactNode;
  children: React.ReactNode;
  position?: "top" | "bottom" | "left" | "right";
  className?: string;
}

export const Tooltip: React.FC<TooltipProps> = ({
  content,
  children,
  position = "top",
  className = "",
}) => {
  const [visible, setVisible] = useState(false);

  const positionClasses = {
    top: "bottom-full left-1/2 -translate-x-1/2 mb-2",
    bottom: "top-full left-1/2 -translate-x-1/2 mt-2",
    left: "right-full top-1/2 -translate-y-1/2 mr-2",
    right: "left-full top-1/2 -translate-y-1/2 ml-2",
  };

  return (
    <div
      className={`relative inline-flex items-center ${className}`}
      onMouseEnter={() => setVisible(true)}
      onMouseLeave={() => setVisible(false)}
      onFocus={() => setVisible(true)}
      onBlur={() => setVisible(false)}
      data-testid="tooltip-container"
    >
      {children}
      {visible && (
        <div
          role="tooltip"
          data-testid="tooltip-bubble"
          className={`absolute z-50 px-2.5 py-1.5 text-[11px] leading-tight text-slate-100 bg-[#0b132b]/95 border border-[#3a506b] rounded-lg shadow-xl backdrop-blur-sm pointer-events-none whitespace-normal min-w-[140px] max-w-[240px] ${positionClasses[position]}`}
        >
          {content}
        </div>
      )}
    </div>
  );
};
