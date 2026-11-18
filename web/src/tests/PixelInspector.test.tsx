import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { PixelInspector } from "../components/PixelInspector";
import { useLayerStore } from "../store/layerStore";

describe("PixelInspector Component", () => {
  beforeEach(() => {
    useLayerStore.setState({
      hoveredCell: null,
      selectedCell: null,
    });
  });

  it("renders placeholder message when no cell is hovered or selected", () => {
    render(<PixelInspector />);
    expect(screen.getByTestId("pixel-inspector")).toBeInTheDocument();
    expect(screen.getByText(/Hover or click a 30m grid cell/i)).toBeInTheDocument();
  });

  it("displays cell coordinates, risk, severity, and spectral chart when cell is selected", () => {
    useLayerStore.setState({
      selectedCell: {
        r: 12,
        c: 34,
        lon: 77.1025,
        lat: 28.6185,
        risk: 0.88,
        severity: 0.72,
        uncertainty: 0.06,
        state: 2,
        days_to_symptoms: 0,
      },
    });

    const handleZoom = vi.fn();
    render(<PixelInspector onZoomToPixel={handleZoom} />);

    expect(screen.getByText("Pixel [12, 34]")).toBeInTheDocument();
    expect(screen.getByText("88.0%")).toBeInTheDocument();
    expect(screen.getByText("72.0%")).toBeInTheDocument();
    expect(screen.getByText("±6.0%")).toBeInTheDocument();
    expect(screen.getByTestId("spectral-chart")).toBeInTheDocument();

    // Zoom to pixel button
    const zoomBtn = screen.getByRole("button", { name: /Zoom to Pixel/i });
    fireEvent.click(zoomBtn);
    expect(handleZoom).toHaveBeenCalledWith(77.1025, 28.6185);

    // Clear selection
    const clearBtn = screen.getByRole("button", { name: /Clear/i });
    fireEvent.click(clearBtn);
    expect(useLayerStore.getState().selectedCell).toBeNull();
  });
});
