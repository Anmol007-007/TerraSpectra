/**
 * Mock Service Worker (MSW) REST handlers for TerraSpectra API endpoints.
 */

import { http, HttpResponse } from "msw";
import mockPredictionData from "./mocks/farm_001_result.json";

export const handlers = [
  // Health check
  http.get("*/api/v1/health", () => {
    return HttpResponse.json({
      status: "ok",
      version: "0.1.0",
      service: "terraspectra-inference-api",
      timestamp: new Date().toISOString(),
    });
  }),

  // Scene metadata
  http.get("*/api/v1/scenes/:sceneId", ({ params }) => {
    const { sceneId } = params;
    return HttpResponse.json({
      scene_id: sceneId,
      farm_id: "farm_001",
      acquisition_date: "2026-11-18T00:00:00Z",
      sensor: "Hyperion-like",
      bands: 224,
      gsd_m: 30.0,
      bounds: [77.0900, 28.6100, 77.1105, 28.6285],
      total_acres: 1000.0,
    });
  }),

  // Prediction results
  http.get("*/api/v1/predict/:sceneId", () => {
    return HttpResponse.json(mockPredictionData);
  }),

  // Trigger forecast run
  http.post("*/api/v1/predict", async ({ request }) => {
    const body = (await request.json().catch(() => ({}))) as Record<string, unknown>;
    return HttpResponse.json(
      {
        job_id: "job_preview_001",
        status: "completed",
        scene_id: body.scene_id || "farm_001",
        result: mockPredictionData,
      },
      { status: 200 }
    );
  }),
];
