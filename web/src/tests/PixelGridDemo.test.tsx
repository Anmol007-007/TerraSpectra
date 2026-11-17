import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { PixelGridDemo } from "../components/PixelGridDemo";

// Mock MapContainer so Deck.gl/react-map-gl GL context is not required in jsdom
vi.mock("../components/MapContainer", () => ({
  MapContainer: () => <div data-testid="mock-map-container">Map Viewport</div>,
}));

describe("PixelGridDemo Component", () => {
  it("renders demo bar and grid specifications", () => {
    render(<PixelGridDemo />);
    expect(screen.getByTestId("pixel-grid-demo")).toBeInTheDocument();
    expect(
      screen.getByText(/30m GSD Hyperspectral Pixel Grid Demo/i)
    ).toBeInTheDocument();
    expect(screen.getByTestId("gsd-badge")).toBeInTheDocument();
  });

  it("toggles between 3D Map viewport and matrix statistics", () => {
    render(<PixelGridDemo />);

    // Switch to matrix stats tab
    const matrixBtn = screen.getByText("Cell Matrix Stats");
    fireEvent.click(matrixBtn);

    expect(screen.getByText("Healthy Canopy")).toBeInTheDocument();
    expect(screen.getByText("Pre-Symptomatic Stress")).toBeInTheDocument();
    expect(screen.getByText("High Risk Blight Hotspot")).toBeInTheDocument();
    expect(
      screen.getByText(/Active Grid Telemetry Sample/i)
    ).toBeInTheDocument();
  });

  it("toggles pixel grid mode on button click", () => {
    render(<PixelGridDemo />);
    const toggleBtn = screen.getByRole("button", {
      name: /Grid Mode:/i,
    });
    expect(toggleBtn).toBeInTheDocument();
    fireEvent.click(toggleBtn);
  });
});
