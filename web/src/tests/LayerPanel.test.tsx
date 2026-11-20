import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { LayerPanel } from "../components/LayerPanel";

describe("LayerPanel component", () => {
  it("renders all GIS layer toggle controls and sliders", () => {
    render(<LayerPanel />);
    expect(screen.getByTestId("layer-panel")).toBeInTheDocument();
    expect(screen.getByText(/1,000-Acre Farm Boundary/i)).toBeInTheDocument();
    expect(screen.getByText(/Agricultural Parcels/i)).toBeInTheDocument();
    expect(screen.getByText(/Disease Risk Heatmap/i)).toBeInTheDocument();
    expect(screen.getByText(/5-Acre Blight Hotspot Zone/i)).toBeInTheDocument();
    expect(screen.getByText(/GCP Calibration Markers/i)).toBeInTheDocument();
    expect(screen.getByText(/Heatmap Opacity/i)).toBeInTheDocument();
    expect(screen.getByText(/3D Topographic Terrain/i)).toBeInTheDocument();
  });

  it("handles camera pitch change and reset view button", () => {
    let resetClicked = false;

    render(
      <LayerPanel
        pitch={30}
        onResetView={() => {
          resetClicked = true;
        }}
      />
    );

    const resetButton = screen.getByRole("button", { name: /Reset 3D Camera View/i });
    resetButton.click();
    expect(resetClicked).toBe(true);
  });
});
