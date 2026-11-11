import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { AppLayout } from "../components/AppLayout";

describe("AppLayout", () => {
  it("renders header and main viewport regions", () => {
    render(
      <AppLayout>
        <div data-testid="map-region">Map viewport</div>
      </AppLayout>
    );
    expect(screen.getByRole("heading", { name: /terraspectra/i })).toBeInTheDocument();
    expect(screen.getByTestId("map-region")).toBeInTheDocument();
  });
});
