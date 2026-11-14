import React from "react";

interface OpacitySliderProps {
  label: string;
  value: number;
  onChange: (val: number) => void;
  min?: number;
  max?: number;
  step?: number;
  accentColor?: string;
}

export const OpacitySlider: React.FC<OpacitySliderProps> = ({
  label,
  value,
  onChange,
  min = 0,
  max = 1,
  step = 0.05,
  accentColor = "accent-[#5bc0be]",
}) => {
  return (
    <div className="py-2">
      <div className="flex justify-between items-center mb-1 text-xs">
        <span className="text-slate-300">{label}</span>
        <span className="text-slate-400 font-mono text-[11px]">
          {Math.round(value * 100)}%
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className={`w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer ${accentColor}`}
      />
    </div>
  );
};
