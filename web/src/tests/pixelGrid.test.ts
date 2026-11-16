import { describe, it, expect } from "vitest";
import { geoToCellIndex, cellToPolygon } from "../utils/heatmap";
import { createPixelGridLayer } from "../layers/pixelGridLayer";
import { useLayerStore } from "../store/layerStore";
import type { PredictionCell } from "../types/heatmap";

describe("Pixel Grid Layer & Coordinate Mapping", () => {
  const bounds: [number, number, number, number] = [77.0900, 28.6100, 77.1105, 28.6285];
  const gridShape: [number, number] = [40, 40];

  it("converts geo coordinates to valid row/col cell index", () => {
    // Center coordinate
    const centerLon = (bounds[0] + bounds[2]) / 2;
    const centerLat = (bounds[1] + bounds[3]) / 2;
    const index = geoToCellIndex(centerLon, centerLat, bounds, gridShape);

    expect(index).not.toBeNull();
    expect(index!.r).toBeGreaterThanOrEqual(18);
    expect(index!.r).toBeLessThanOrEqual(22);
    expect(index!.c).toBeGreaterThanOrEqual(18);
    expect(index!.c).toBeLessThanOrEqual(22);
  });

  it("returns null for coordinates outside farm boundary", () => {
    const outside = geoToCellIndex(10.0, 10.0, bounds, gridShape);
    expect(outside).toBeNull();
  });

  it("generates closed 5-point polygon for a 30m GSD cell", () => {
    const cell: PredictionCell = {
      r: 20,
      c: 20,
      lon: 77.1000,
      lat: 28.6200,
      risk: 0.75,
      severity: 0.60,
      uncertainty: 0.08,
      state: 1,
    };
    const poly = cellToPolygon(cell, 30);
    expect(poly.length).toBe(5);
    // Closed polygon: first point matches last point
    expect(poly[0][0]).toBeCloseTo(poly[4][0], 6);
    expect(poly[0][1]).toBeCloseTo(poly[4][1], 6);
  });

  it("creates interactive Deck.gl PixelGridLayer with 30m cell size and picking", () => {
    const cells: PredictionCell[] = [
      { r: 0, c: 0, lon: 77.1, lat: 28.6, risk: 0.2, severity: 0.1, uncertainty: 0.05, state: 0 },
      { r: 1, c: 1, lon: 77.101, lat: 28.601, risk: 0.85, severity: 0.7, uncertainty: 0.09, state: 2 },
    ];
    const layer = createPixelGridLayer({
      data: cells,
      opacity: 0.9,
      riskThreshold: 0.0,
      selectedCell: cells[1],
    });

    expect(layer.id).toBe("layer-pixel-grid");
    expect(layer.props.cellSize).toBe(30);
    expect(layer.props.pickable).toBe(true);
    expect(layer.props.extruded).toBe(true);
  });

  it("stores and clears selected and hovered cell in layerStore", () => {
    const store = useLayerStore.getState();
    const cell: PredictionCell = {
      r: 5,
      c: 12,
      lon: 77.102,
      lat: 28.615,
      risk: 0.82,
      severity: 0.65,
      uncertainty: 0.07,
      state: 1,
    };

    store.setHoveredCell(cell);
    expect(useLayerStore.getState().hoveredCell).toEqual(cell);

    store.setSelectedCell(cell);
    expect(useLayerStore.getState().selectedCell).toEqual(cell);

    store.setSelectedCell(null);
    expect(useLayerStore.getState().selectedCell).toBeNull();
  });
});
