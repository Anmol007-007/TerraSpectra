import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../api/client";

export interface SceneMetadata {
  scene_id: string;
  farm_id: string;
  acquisition_date: string;
  sensor: string;
  bands: number;
  gsd_m: number;
  bounds: [number, number, number, number];
  total_acres: number;
}

export function useScene(sceneId: string = "farm_001") {
  return useQuery<SceneMetadata>({
    queryKey: ["scene", sceneId],
    queryFn: () => apiClient<SceneMetadata>(`/api/v1/scenes/${sceneId}`),
  });
}
