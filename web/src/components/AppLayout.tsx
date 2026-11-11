import React from "react";
import { Header } from "./Header";
import { Sidebar } from "./Sidebar";

interface AppLayoutProps {
  children?: React.ReactNode;
  rightPanel?: React.ReactNode;
  bottomBar?: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({
  children,
  rightPanel,
  bottomBar,
}) => {
  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-[#0b132b] text-slate-100">
      <Header />
      <div className="flex flex-1 overflow-hidden relative">
        <Sidebar />
        <main className="flex-1 relative flex flex-col overflow-hidden">
          <div className="flex-1 relative">{children}</div>
          {bottomBar && <div className="h-20 border-t border-[#3a506b] bg-[#141d36]">{bottomBar}</div>}
        </main>
        {rightPanel && (
          <aside className="w-80 border-l border-[#3a506b] bg-[#141d36] overflow-y-auto">
            {rightPanel}
          </aside>
        )}
      </div>
    </div>
  );
};
