import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import React from "react";
import { BaseMap } from "../components/BaseMap";

// Mock react-map-gl
vi.mock("react-map-gl", () => {
  return {
    default: ({ children }: { children?: React.ReactNode }) => (
      <div data-testid="mocked-react-map">{children}</div>
    ),
    NavigationControl: () => <div data-testid="mock-nav-control" />,
    ScaleControl: () => <div data-testid="mock-scale-control" />,
  };
});

describe("BaseMap component", () => {
  it("renders map container and style switcher", () => {
    render(<BaseMap />);
    expect(screen.getByTestId("base-map-container")).toBeInTheDocument();
    expect(screen.getByTestId("mocked-react-map")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /satellite/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /streets/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /dark/i })).toBeInTheDocument();
  });
});
