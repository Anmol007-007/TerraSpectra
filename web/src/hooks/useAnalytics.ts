import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../api/client";
import type { AnalyticsSummaryData } from "../types/analytics";
import mockAnalyticsData from "../api/mocks/analytics.json";
import { usePrediction } from "./usePrediction";
import { computeAcreageFromCells, getDistributionFromBreakdown } from "../utils/acres";

const FALLBACK_ANALYTICS = mockAnalyticsData as unknown as AnalyticsSummaryData;

/**
 * Hook to retrieve and select farm analytics summary data,
 * dynamically combining live raster predictions with mock analytics scenarios.
 */
export function useAnalytics(sceneId: string = "farm_001") {
  const { data: predictionData, isLoading: predictionLoading } = usePrediction(sceneId);

  const query = useQuery<AnalyticsSummaryData>({
    queryKey: ["analytics", sceneId],
    queryFn: async () => {
      try {
        return await apiClient<AnalyticsSummaryData>(`/api/v1/analytics/${sceneId}`);
      } catch {
        return FALLBACK_ANALYTICS;
      }
    },
  });

  const rawData = query.data ?? FALLBACK_ANALYTICS;

  // If live cell predictions exist, compute real-time acreage breakdown
  let mergedData: AnalyticsSummaryData = rawData;
  if (predictionData && predictionData.cells && predictionData.cells.length > 0) {
    const computedBreakdown = computeAcreageFromCells(
      predictionData.cells,
      predictionData.cell_size_m || 30
    );
    const distribution = getDistributionFromBreakdown(computedBreakdown);

    mergedData = {
      ...rawData,
      sceneId: predictionData.scene_id || rawData.sceneId,
      farmId: predictionData.farm_id || rawData.farmId,
      forecastHorizonDays: predictionData.forecast_horizon_days || rawData.forecastHorizonDays,
      totalAcres: computedBreakdown.totalAcres,
      acresAtRisk: computedBreakdown.stressedAcres + computedBreakdown.diseasedAcres,
      hotspot5AcreDetected: predictionData.hotspot_5acre_detected ?? rawData.hotspot5AcreDetected,
      hotspotAcres: predictionData.hotspot_acres ?? rawData.hotspotAcres,
      breakdown: computedBreakdown,
      distribution,
    };
  }

  return {
    data: mergedData,
    isLoading: query.isLoading || predictionLoading,
    isError: query.isError,
    error: query.error,
    refetch: query.refetch,
  };
}
