import React from "react";

interface ToggleSwitchProps {
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  badge?: string;
  badgeColor?: string;
}

export const ToggleSwitch: React.FC<ToggleSwitchProps> = ({
  label,
  checked,
  onChange,
  badge,
  badgeColor = "bg-[#5bc0be]",
}) => {
  return (
    <label className="flex items-center justify-between py-1.5 cursor-pointer select-none group">
      <div className="flex items-center space-x-2">
        <span className="text-xs text-slate-200 group-hover:text-white transition-colors">
          {label}
        </span>
        {badge && (
          <span
            className={`text-[10px] px-1.5 py-0.5 rounded-full text-[#0b132b] font-bold ${badgeColor}`}
          >
            {badge}
          </span>
        )}
      </div>

      <div
        onClick={() => onChange(!checked)}
        className={`w-9 h-5 flex items-center rounded-full p-1 transition-colors duration-200 ease-in-out ${
          checked ? "bg-[#5bc0be]" : "bg-slate-700"
        }`}
      >
        <div
          className={`bg-white w-3.5 h-3.5 rounded-full shadow-md transform transition-transform duration-200 ease-in-out ${
            checked ? "translate-x-4" : "translate-x-0"
          }`}
        />
      </div>
    </label>
  );
};
