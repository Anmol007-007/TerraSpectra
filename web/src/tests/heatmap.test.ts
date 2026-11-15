import { describe, it, expect } from "vitest";
import mockResult from "../api/mocks/farm_001_result.json";
import { parseResult } from "../api/schemas/resultSchema";
import { riskToRgba, filterCellsByThreshold } from "../utils/heatmap";
import type { PredictionCell } from "../types/heatmap";

describe("Heatmap & Prediction Contract", () => {
  it("validates mock prediction payload against Zod schema", () => {
    const parsed = parseResult(mockResult);
    expect(parsed.farm_id).toBe("farm_001");
    expect(parsed.hotspot_5acre_detected).toBe(true);
    expect(parsed.cells.length).toBeGreaterThan(0);
    expect(parsed.summary.high_risk_acreage).toBeGreaterThan(0);
  });

  it("maps healthy risk (0.1) to green RGBA values", () => {
    const rgba = riskToRgba(0.1, 0.85);
    // Green channel should dominate
    expect(rgba[1]).toBeGreaterThan(rgba[0]); // g > r
    expect(rgba[3]).toBe(Math.round(0.85 * 255));
  });

  it("maps pre-symptomatic stress risk (0.45) to amber RGBA values", () => {
    const rgba = riskToRgba(0.45, 0.85);
    // High red and high green creates amber/yellow
    expect(rgba[0]).toBe(245);
    expect(rgba[1]).toBeGreaterThan(100);
    expect(rgba[2]).toBeLessThan(50);
  });

  it("maps severe blight risk (0.95) to red RGBA values", () => {
    const rgba = riskToRgba(0.95, 1.0);
    // Strong red, low green and blue
    expect(rgba[0]).toBeGreaterThan(120);
    expect(rgba[1]).toBeLessThan(70);
    expect(rgba[3]).toBe(255);
  });

  it("filters cells according to risk cutoff threshold", () => {
    const cells: PredictionCell[] = [
      { r: 0, c: 0, lon: 77.1, lat: 28.6, risk: 0.1, severity: 0.05, uncertainty: 0.02, state: 0 },
      { r: 1, c: 1, lon: 77.1, lat: 28.6, risk: 0.4, severity: 0.2, uncertainty: 0.05, state: 1 },
      { r: 2, c: 2, lon: 77.1, lat: 28.6, risk: 0.8, severity: 0.7, uncertainty: 0.08, state: 2 },
    ];
    const filtered = filterCellsByThreshold(cells, 0.35);
    expect(filtered.length).toBe(2);
    expect(filtered[0].risk).toBe(0.4);
    expect(filtered[1].risk).toBe(0.8);
  });
});
