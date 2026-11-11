import { describe, it, expect } from "vitest";
import { acresToM2, m2ToAcres, pixelsToAcres, acresToPixels } from "../utils/acres";
import { formatAcres, formatPercent } from "../utils/format";

describe("acres utilities", () => {
  it("converts m2 to acres and back accurately", () => {
    const acres = 5.0;
    const m2 = acresToM2(acres);
    expect(m2ToAcres(m2)).toBeCloseTo(acres, 4);
  });

  it("calculates 5-acre hotspot to ~22.5 pixels at 30m GSD", () => {
    const px = acresToPixels(5.0, 30.0);
    expect(Math.round(px)).toBe(22);
    expect(pixelsToAcres(px, 30.0)).toBeCloseTo(5.0, 3);
  });
});

describe("format utilities", () => {
  it("formats acres and percentages", () => {
    expect(formatAcres(5.12)).toBe("5.1 ac");
    expect(formatPercent(0.854)).toBe("85%");
  });
});
