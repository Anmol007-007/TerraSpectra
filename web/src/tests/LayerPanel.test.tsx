import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import React from "react";
import { LayerPanel } from "../components/LayerPanel";

describe("LayerPanel component", () => {
  it("renders all GIS layer toggle controls and sliders", () => {
    render(<LayerPanel />);
    expect(screen.getByTestId("layer-panel")).toBeInTheDocument();
    expect(screen.getByText(/1,000-Acre Farm Boundary/i)).toBeInTheDocument();
    expect(screen.getByText(/Agricultural Parcels/i)).toBeInTheDocument();
    expect(screen.getByText(/Disease Risk Heatmap/i)).toBeInTheDocument();
    expect(screen.getByText(/5-Acre Blight Hotspot Zone/i)).toBeInTheDocument();
    expect(screen.getByText(/Heatmap Opacity/i)).toBeInTheDocument();
  });
});
