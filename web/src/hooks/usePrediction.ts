import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../api/client";
import type { FarmPredictionResult } from "../types/heatmap";
import mockPredictionData from "../api/mocks/farm_001_result.json";

const FALLBACK_RESULT = mockPredictionData as unknown as FarmPredictionResult;

export function usePrediction(sceneId: string = "farm_001") {
  const queryClient = useQueryClient();

  const query = useQuery<FarmPredictionResult>({
    queryKey: ["prediction", sceneId],
    queryFn: async () => {
      try {
        return await apiClient<FarmPredictionResult>(`/api/v1/predict/${sceneId}`);
      } catch {
        // Fallback to bundled synthetic prediction scenario when API server is offline
        return FALLBACK_RESULT;
      }
    },
  });

  const mutation = useMutation({
    mutationFn: async () => {
      try {
        return await apiClient<{ result: FarmPredictionResult }>("/api/v1/predict", {
          method: "POST",
          body: JSON.stringify({ scene_id: sceneId }),
        });
      } catch {
        return { result: FALLBACK_RESULT };
      }
    },
    onSuccess: (data) => {
      queryClient.setQueryData(["prediction", sceneId], data.result);
    },
  });

  return {
    data: query.data ?? FALLBACK_RESULT,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    refetch: query.refetch,
    runForecast: mutation.mutate,
    isForecasting: mutation.isPending,
  };
}
