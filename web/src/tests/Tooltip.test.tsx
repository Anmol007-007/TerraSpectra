import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { Tooltip } from "../components/Tooltip";

describe("Tooltip Component", () => {
  it("renders children without showing tooltip bubble initially", () => {
    render(
      <Tooltip content="Tooltip explanation text">
        <button>Hover me</button>
      </Tooltip>
    );

    expect(screen.getByText("Hover me")).toBeInTheDocument();
    expect(screen.queryByRole("tooltip")).toBeNull();
  });

  it("displays tooltip bubble on mouse enter and hides on mouse leave", () => {
    render(
      <Tooltip content="Fungal Blight Risk Factor">
        <span>Hover Target</span>
      </Tooltip>
    );

    const container = screen.getByTestId("tooltip-container");
    fireEvent.mouseEnter(container);

    expect(screen.getByRole("tooltip")).toBeInTheDocument();
    expect(screen.getByText("Fungal Blight Risk Factor")).toBeInTheDocument();

    fireEvent.mouseLeave(container);
    expect(screen.queryByRole("tooltip")).toBeNull();
  });
});
