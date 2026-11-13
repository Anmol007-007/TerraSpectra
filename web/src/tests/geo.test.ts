import { describe, it, expect } from "vitest";
import { FARM_BOUNDS, fitBounds } from "../utils/geo";

describe("fitBounds utility", () => {
  it("calculates farm center and appropriate zoom level", () => {
    const view = fitBounds(FARM_BOUNDS, 1024, 768);
    expect(view.longitude).toBeCloseTo(77.10025, 4);
    expect(view.latitude).toBeCloseTo(28.61925, 4);
    expect(view.zoom).toBeGreaterThanOrEqual(13);
    expect(view.zoom).toBeLessThanOrEqual(16);
  });

  it("handles standard bounding boxes gracefully", () => {
    const b = { minLon: 0, minLat: 0, maxLon: 1, maxLat: 1 };
    const view = fitBounds(b, 800, 600);
    expect(view.longitude).toBe(0.5);
    expect(view.latitude).toBe(0.5);
  });
});
