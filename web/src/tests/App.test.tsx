import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import App from "../App";

describe("App", () => {
  it("renders the TerraSpectra header", () => {
    render(<App />);
    expect(screen.getByRole("heading", { name: /terraspectra/i })).toBeInTheDocument();
  });

  it("renders the map placeholder", () => {
    render(<App />);
    expect(screen.getByText(/Map placeholder/i)).toBeInTheDocument();
  });
});

