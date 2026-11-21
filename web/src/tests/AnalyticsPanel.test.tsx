import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AnalyticsPanel } from "../components/panels/AnalyticsPanel";
import { RightSidebar } from "../components/layout/RightSidebar";

// Mock recharts ResponsiveContainer to avoid size measuring issues in jsdom
vi.mock("recharts", async () => {
  const original = await vi.importActual<Record<string, unknown>>("recharts");
  return {
    ...original,
    ResponsiveContainer: ({ children }: { children: React.ReactNode }) => (
      <div style={{ width: 400, height: 200 }}>{children}</div>
    ),
  };
});

function renderWithClient(ui: React.ReactElement) {
  const testClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });
  return render(<QueryClientProvider client={testClient}>{ui}</QueryClientProvider>);
}

describe("AnalyticsPanel", () => {
  it("renders analytics panel with farm title and KPI cards", async () => {
    renderWithClient(<AnalyticsPanel sceneId="farm_001" />);

    expect(await screen.findByText(/Crop Health Analytics/i)).toBeInTheDocument();
    expect(await screen.findByTestId("kpi-grid")).toBeInTheDocument();
    expect(await screen.findByText(/Total Farm/i)).toBeInTheDocument();
    expect(await screen.findByText(/At-Risk Area/i)).toBeInTheDocument();
    expect(await screen.findByText(/5-Acre Hotspot/i)).toBeInTheDocument();
  });

  it("renders 5-acre blight hotspot alert banner", async () => {
    renderWithClient(<AnalyticsPanel sceneId="farm_001" />);

    expect(await screen.findByTestId("hotspot-alert-banner")).toBeInTheDocument();
    expect(await screen.findByText(/5-Acre Blight Hotspot Detected/i)).toBeInTheDocument();
  });

  it("switches tabs between Overview, Acreage table, and Spectral anomalies", async () => {
    renderWithClient(<AnalyticsPanel sceneId="farm_001" />);

    // Default tab is overview
    expect(await screen.findByTestId("tab-overview")).toBeInTheDocument();

    // Switch to Acreage tab
    const acreageTab = await screen.findByRole("tab", { name: /acreage/i });
    fireEvent.click(acreageTab);
    expect(await screen.findByTestId("tab-acreage")).toBeInTheDocument();
    expect(await screen.findByText(/Healthy Crop/i)).toBeInTheDocument();

    // Switch to Spectral tab
    const spectralTab = await screen.findByRole("tab", { name: /spectral/i });
    fireEvent.click(spectralTab);
    expect(await screen.findByTestId("tab-anomalies")).toBeInTheDocument();
    expect(await screen.findByText(/Red-Edge Shift/i)).toBeInTheDocument();
  });
});

describe("RightSidebar", () => {
  it("renders collapsible right sidebar and toggles open state", async () => {
    renderWithClient(<RightSidebar />);

    const sidebar = await screen.findByTestId("right-sidebar");
    expect(sidebar).toBeInTheDocument();

    const toggleBtn = await screen.findByTestId("toggle-analytics-btn");
    expect(toggleBtn).toBeInTheDocument();

    // Toggle collapse
    fireEvent.click(toggleBtn);
    expect(await screen.findByText(/Analytics & KPIs/i)).toBeInTheDocument();

    // Toggle expand
    fireEvent.click(toggleBtn);
    expect(await screen.findByText(/Crop Health Analytics/i)).toBeInTheDocument();
  });
});
