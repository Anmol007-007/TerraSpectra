import React from "react";
import { useUiStore, type ToastMessage } from "../store/uiStore";

export const ToastContainer: React.FC = () => {
  const { toasts, removeToast } = useUiStore();

  if (toasts.length === 0) {
    return null;
  }

  const typeStyles: Record<ToastMessage["type"], string> = {
    info: "bg-[#1c2541] border-[#5bc0be] text-slate-100",
    success: "bg-emerald-950 border-emerald-500 text-emerald-100",
    warning: "bg-amber-950 border-amber-500 text-amber-100",
    error: "bg-red-950 border-red-500 text-red-100",
  };

  const typeIcons: Record<ToastMessage["type"], string> = {
    info: "ℹ️",
    success: "✅",
    warning: "⚠️",
    error: "❌",
  };

  return (
    <div
      data-testid="toast-container"
      className="fixed bottom-6 right-6 z-50 flex flex-col space-y-2 pointer-events-none"
    >
      {toasts.map((toast) => (
        <div
          key={toast.id}
          data-testid="toast-item"
          className={`pointer-events-auto flex items-center space-x-3 px-4 py-2.5 rounded-lg border shadow-2xl text-xs max-w-sm backdrop-blur-md transition-all ${
            typeStyles[toast.type]
          }`}
        >
          <span>{typeIcons[toast.type]}</span>
          <span className="flex-1 font-medium">{toast.message}</span>
          <button
            onClick={() => removeToast(toast.id)}
            className="text-slate-400 hover:text-white ml-2 text-sm"
          >
            ×
          </button>
        </div>
      ))}
    </div>
  );
};
