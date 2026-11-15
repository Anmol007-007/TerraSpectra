import { z } from "zod";
import type { FarmPredictionResult } from "../../types/heatmap";

export const cropStateSchema = z.union([z.literal(0), z.literal(1), z.literal(2)]);

export const predictionCellSchema = z.object({
  r: z.number().int().nonnegative(),
  c: z.number().int().nonnegative(),
  lon: z.number(),
  lat: z.number(),
  risk: z.number().min(0).max(1),
  severity: z.number().min(0).max(1),
  uncertainty: z.number().min(0).max(1),
  state: cropStateSchema,
  days_to_symptoms: z.number().optional(),
});

export const farmPredictionSummarySchema = z.object({
  healthy_pct: z.number().min(0).max(100),
  pre_symptomatic_pct: z.number().min(0).max(100),
  diseased_pct: z.number().min(0).max(100),
  mean_uncertainty: z.number().min(0).max(1),
  high_risk_pixel_count: z.number().int().nonnegative(),
  high_risk_acreage: z.number().nonnegative(),
});

export const farmPredictionResultSchema = z.object({
  scene_id: z.string(),
  farm_id: z.string(),
  timestamp: z.string(),
  forecast_horizon_days: z.number().default(21),
  grid_shape: z.tuple([z.number().int().positive(), z.number().int().positive()]),
  cell_size_m: z.number().positive().default(30),
  bounds: z.tuple([z.number(), z.number(), z.number(), z.number()]),
  hotspot_5acre_detected: z.boolean(),
  hotspot_acres: z.number().nonnegative(),
  summary: farmPredictionSummarySchema,
  cells: z.array(predictionCellSchema),
});

export function parseResult(data: unknown): FarmPredictionResult {
  return farmPredictionResultSchema.parse(data) as FarmPredictionResult;
}
