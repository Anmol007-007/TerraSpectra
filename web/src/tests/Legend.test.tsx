import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { Legend } from "../components/Legend";

describe("Legend Component", () => {
  it("renders risk scale gradient and classification categories", () => {
    render(<Legend hotspotDetected={true} hotspotAcres={5.4} />);

    expect(screen.getByTestId("disease-legend")).toBeInTheDocument();
    expect(screen.getByText(/Disease Risk Scale/i)).toBeInTheDocument();
    expect(screen.getByText(/Healthy \(Baseline Chlorophyll\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Pre-symptomatic Stress \(21-Day Forecast\)/i)).toBeInTheDocument();
    expect(screen.getByText(/High Blight Risk \(5-Acre Hotspot\)/i)).toBeInTheDocument();
    expect(screen.getByText(/5.4 Ac Alert/i)).toBeInTheDocument();
  });

  it("omits alert badge when no hotspot is detected", () => {
    render(<Legend hotspotDetected={false} />);
    expect(screen.queryByText(/Ac Alert/i)).not.toBeInTheDocument();
  });
});
