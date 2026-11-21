import { describe, it, expect } from "vitest";
import {
  m2ToAcres,
  acresToM2,
  pixelsToAcres,
  acresToPixels,
  computeAcreageFromCells,
  getDistributionFromBreakdown,
} from "../utils/acres";

describe("acres utilities", () => {
  it("converts m2 to acres and back accurately", () => {
    const areaM2 = 4046.8564; // exactly 1 acre
    const acres = m2ToAcres(areaM2);
    expect(acres).toBeCloseTo(1.0, 4);

    const m2Back = acresToM2(acres);
    expect(m2Back).toBeCloseTo(areaM2, 4);
  });

  it("converts pixels to acres for 30m Hyperion GSD", () => {
    // 1 pixel = 900 m2 ≈ 0.2223948 acres
    const singlePixelAcres = pixelsToAcres(1, 30);
    expect(singlePixelAcres).toBeCloseTo(0.2224, 3);

    // 5 acres ≈ 22.48 pixels
    const pixelsFor5Acres = acresToPixels(5, 30);
    expect(Math.round(pixelsFor5Acres)).toBe(22);
  });

  it("computes acreage breakdown from classified cells", () => {
    // 100 cells: 70 healthy (0), 20 stressed (1), 10 diseased (2)
    const cells: Array<{ state: number }> = [
      ...Array.from({ length: 70 }, () => ({ state: 0 })),
      ...Array.from({ length: 20 }, () => ({ state: 1 })),
      ...Array.from({ length: 10 }, () => ({ state: 2 })),
    ];

    const breakdown = computeAcreageFromCells(cells, 30);

    expect(breakdown.healthyPct).toBe(70.0);
    expect(breakdown.stressedPct).toBe(20.0);
    expect(breakdown.diseasedPct).toBe(10.0);
    expect(breakdown.totalAcres).toBeCloseTo(22.24, 1);
    expect(breakdown.healthyAcres + breakdown.stressedAcres + breakdown.diseasedAcres).toBeCloseTo(
      breakdown.totalAcres,
      1
    );
  });

  it("handles empty cell list safely", () => {
    const breakdown = computeAcreageFromCells([]);
    expect(breakdown.totalAcres).toBe(0);
    expect(breakdown.healthyPct).toBe(0);
  });

  it("generates chart distribution items correctly", () => {
    const breakdown = {
      totalAcres: 100,
      healthyAcres: 80,
      stressedAcres: 15,
      diseasedAcres: 5,
      healthyPct: 80,
      stressedPct: 15,
      diseasedPct: 5,
    };
    const dist = getDistributionFromBreakdown(breakdown);
    expect(dist).toHaveLength(3);
    expect(dist[0].state).toBe("healthy");
    expect(dist[0].acres).toBe(80);
    expect(dist[1].state).toBe("stressed");
    expect(dist[2].state).toBe("diseased");
  });
});
