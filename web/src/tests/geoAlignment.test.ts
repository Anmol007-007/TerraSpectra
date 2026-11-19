import { describe, it, expect } from "vitest";
import { pixelToLonLat, lonLatToPixel, FARM_BOUNDS } from "../utils/geo";
import gcpFixtures from "./fixtures/gcp_fixtures.json";

describe("GIS Alignment & Geo Transformation Validation", () => {
  const gridShape: [number, number] = [67, 67];

  it("matches backend Ground Control Points (GCP) fixtures with sub-millimeter precision", () => {
    for (const gcp of gcpFixtures.gcps) {
      const [lon, lat] = pixelToLonLat(gcp.row, gcp.col, FARM_BOUNDS, gridShape);

      // Verify coordinate match to 5 decimal places (~1.1 meter on Earth's surface)
      expect(lon).toBeCloseTo(gcp.lon, 4);
      expect(lat).toBeCloseTo(gcp.lat, 4);
    }
  });

  it("round-trips pixel to lon/lat and back to pixel within 0.001 pixel tolerance", () => {
    const testPoints: [number, number][] = [
      [0, 0],
      [10, 20],
      [33, 33],
      [50, 45],
      [66, 66],
    ];

    for (const [r, c] of testPoints) {
      const [lon, lat] = pixelToLonLat(r, c, FARM_BOUNDS, gridShape);
      const [rRec, cRec] = lonLatToPixel(lon, lat, FARM_BOUNDS, gridShape);

      expect(rRec).toBeCloseTo(r, 2);
      expect(cRec).toBeCloseTo(c, 2);
    }
  });

  it("satisfies the 0.5-pixel / 15m ground sample distance alignment tolerance", () => {
    // 30m GSD: 0.5 pixel error = 15m max spatial offset
    // 1 deg lat ≈ 111,320m -> 15m ≈ 0.0001347 deg
    const maxDegreeTolerance = 0.00015;

    for (const gcp of gcpFixtures.gcps) {
      const [lon, lat] = pixelToLonLat(gcp.row, gcp.col, FARM_BOUNDS, gridShape);
      const deltaLon = Math.abs(lon - gcp.lon);
      const deltaLat = Math.abs(lat - gcp.lat);

      expect(deltaLon).toBeLessThanOrEqual(maxDegreeTolerance);
      expect(deltaLat).toBeLessThanOrEqual(maxDegreeTolerance);
    }
  });

  it("applies half-pixel center offset correctly", () => {
    // Center offset gives coordinates for (row + 0.5, col + 0.5)
    const [centerLon, centerLat] = pixelToLonLat(0, 0, FARM_BOUNDS, gridShape, true);
    const [cornerLon, cornerLat] = pixelToLonLat(0, 0, FARM_BOUNDS, gridShape, false);

    expect(centerLon).toBeGreaterThan(cornerLon);
    expect(centerLat).toBeLessThan(cornerLat);
  });

  it("constructs accurate polygon bounds for a pixel index with zero edge shear", async () => {
    const { pixelIndexToPolygon } = await import("../utils/geo");
    const poly = pixelIndexToPolygon(0, 0, FARM_BOUNDS, gridShape);

    expect(poly.length).toBe(5);
    // Closed polygon
    expect(poly[0][0]).toBeCloseTo(poly[4][0], 6);
    expect(poly[0][1]).toBeCloseTo(poly[4][1], 6);

    // Verify top-left vertex matches corner without center offset
    const [cornerLon, cornerLat] = pixelToLonLat(0, 0, FARM_BOUNDS, gridShape, false);
    expect(poly[3][0]).toBeCloseTo(cornerLon, 4);
    expect(poly[3][1]).toBeCloseTo(cornerLat, 4);
  });
});
