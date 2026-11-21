import React, { useState } from "react";
import { useAnalytics } from "../../hooks/useAnalytics";
import { StatCard } from "../common/StatCard";
import { Tabs } from "../common/Tabs";
import { AcreageDistributionChart } from "../charts/AcreageDistributionChart";
import { EmptyState } from "../common/EmptyState";
import { RISK_COLORS } from "../../utils/tokens";

export interface AnalyticsPanelProps {
  sceneId?: string;
  onRefresh?: () => void;
}

export const AnalyticsPanel: React.FC<AnalyticsPanelProps> = ({
  sceneId = "farm_001",
  onRefresh,
}) => {
  const { data, isLoading, isError, refetch } = useAnalytics(sceneId);
  const [activeTab, setActiveTab] = useState<string>("overview");

  const tabs = [
    { id: "overview", label: "Overview" },
    { id: "acreage", label: "Acreage" },
    { id: "anomalies", label: "Spectral", count: data.anomalies.length },
  ];

  const handleRefresh = () => {
    void refetch();
    if (onRefresh) onRefresh();
  };

  if (isError) {
    return (
      <div className="p-4" data-testid="analytics-error">
        <EmptyState
          title="Failed to Load Analytics"
          message="Could not retrieve farm analytics data. Please check connection and try again."
          actionLabel="Retry"
          onAction={handleRefresh}
        />
      </div>
    );
  }

  return (
    <div
      className="p-4 flex flex-col space-y-4 text-slate-100 h-full overflow-y-auto"
      data-testid="analytics-panel"
    >
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[#3a506b]/40 pb-2">
        <div>
          <h3 className="text-sm font-bold text-white flex items-center space-x-1.5">
            <span>Crop Health Analytics</span>
          </h3>
          <p className="text-[11px] text-slate-400 mt-0.5">
            Farm: <span className="text-[#5bc0be] font-medium">{data.farmId}</span>
          </p>
        </div>
        <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded bg-[#5bc0be]/20 text-[#5bc0be] border border-[#5bc0be]/40">
          {data.forecastHorizonDays}d Lead Time
        </span>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 gap-2" data-testid="kpi-grid">
        <StatCard
          title="Total Farm"
          value={data.totalAcres}
          unit="ac"
          subtitle="1,000-acre baseline"
          loading={isLoading}
        />
        <StatCard
          title="At-Risk Area"
          value={data.acresAtRisk}
          unit="ac"
          subtitle="Pre-symptomatic + blight"
          trend={{
            value: data.hotspot5AcreDetected ? "Alert" : "Normal",
            isWarning: data.hotspot5AcreDetected,
          }}
          indicatorColor={data.hotspot5AcreDetected ? RISK_COLORS.DISEASED : RISK_COLORS.STRESSED}
          loading={isLoading}
        />
        <StatCard
          title="5-Acre Hotspot"
          value={data.hotspot5AcreDetected ? `${data.hotspotAcres} ac` : "None"}
          subtitle="Target Blight Risk Zone"
          indicatorColor={data.hotspot5AcreDetected ? RISK_COLORS.DISEASED : RISK_COLORS.HEALTHY}
          loading={isLoading}
        />
        <StatCard
          title="Model Uncertainty"
          value={data.meanUncertainty}
          unit="std"
          subtitle="MC-Dropout variance"
          loading={isLoading}
        />
      </div>

      {/* Hotspot Alert Banner */}
      {data.hotspot5AcreDetected && (
        <div
          className="p-3 bg-red-950/40 border border-red-500/50 rounded-lg flex items-start space-x-2 text-xs"
          data-testid="hotspot-alert-banner"
        >
          <span className="text-red-400 text-base leading-none">⚠️</span>
          <div>
            <span className="font-semibold text-red-200">5-Acre Blight Hotspot Detected</span>
            <p className="text-[11px] text-red-300/80 mt-0.5">
              Fungal blight forecasted ~21 days ahead of visible symptoms. Targeted fungicide
              spraying recommended for immediate intervention.
            </p>
          </div>
        </div>
      )}

      {/* Tabs */}
      <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} />

      {/* Tab Content */}
      {activeTab === "overview" && (
        <div className="space-y-4" data-testid="tab-overview">
          <AcreageDistributionChart data={data.distribution} />
        </div>
      )}

      {activeTab === "acreage" && (
        <div className="space-y-3" data-testid="tab-acreage">
          <div className="bg-[#1f2a4a]/40 rounded-lg border border-[#3a506b]/40 overflow-hidden">
            <table className="w-full text-xs">
              <thead className="bg-[#141d36] text-slate-400 border-b border-[#3a506b]/40">
                <tr>
                  <th className="text-left p-2">Status</th>
                  <th className="text-right p-2">Acres</th>
                  <th className="text-right p-2">Share</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#3a506b]/20">
                {data.distribution.map((item) => (
                  <tr key={item.state} className="hover:bg-[#1f2a4a]/60">
                    <td className="p-2 flex items-center space-x-2">
                      <span
                        className="w-2.5 h-2.5 rounded-full shrink-0"
                        style={{ backgroundColor: item.color }}
                      />
                      <span className="text-slate-200">{item.label}</span>
                    </td>
                    <td className="p-2 text-right font-mono text-white font-semibold">
                      {item.acres}
                    </td>
                    <td className="p-2 text-right font-mono text-[#5bc0be]">
                      {item.percentage}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === "anomalies" && (
        <div className="space-y-2" data-testid="tab-anomalies">
          {data.anomalies.length === 0 ? (
            <EmptyState
              title="No Anomalies Detected"
              message="Hyperspectral bands reflect standard vegetative baseline."
            />
          ) : (
            data.anomalies.map((anom) => (
              <div
                key={anom.id}
                className="p-2.5 bg-[#1f2a4a]/60 rounded-lg border border-[#3a506b]/40 text-xs flex flex-col space-y-1"
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-slate-200">{anom.label}</span>
                  <span
                    className={`text-[10px] font-bold uppercase px-1.5 py-0.2 rounded ${
                      anom.severity === "high"
                        ? "bg-red-500/20 text-red-400"
                        : anom.severity === "medium"
                        ? "bg-amber-500/20 text-amber-400"
                        : "bg-blue-500/20 text-blue-400"
                    }`}
                  >
                    {anom.severity}
                  </span>
                </div>
                <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono">
                  <span>Wavelength: {anom.wavelength_nm} nm</span>
                  <span className={anom.delta < 0 ? "text-red-400" : "text-emerald-400"}>
                    Δ {anom.delta > 0 ? `+${anom.delta}` : anom.delta}
                  </span>
                </div>
                <div className="text-[10px] text-slate-400">
                  Affected: <span className="text-white font-semibold">{anom.affectedAcres} ac</span>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};
