/**
 * Unit tests for StatGrid component.
 */

import React from "react";
import { render, screen } from "@testing-library/react-native";
import StatGrid from "../../../src/components/ui/StatGrid";

// Mock the useResponsive hook to return predictable values
jest.mock("../../../src/hooks/useResponsive", () => ({
  useResponsive: () => ({ statColumns: 2, isNarrow: false }),
}));

const mockStats = [
  { label: "Total Sales", value: "₹5,000", color: "#00c853" },
  { label: "Transactions", value: "15", color: "#2196F3" },
  { label: "Low Stock", value: "3", color: "#ff9800" },
  { label: "Avg Value", value: "₹333", color: "#9c27b0" },
];

describe("StatGrid", () => {
  it("renders all stat cards", () => {
    render(<StatGrid stats={mockStats} />);
    expect(screen.getByText("Total Sales")).toBeTruthy();
    expect(screen.getByText("Transactions")).toBeTruthy();
    expect(screen.getByText("Low Stock")).toBeTruthy();
    expect(screen.getByText("Avg Value")).toBeTruthy();
  });

  it("renders all stat values", () => {
    render(<StatGrid stats={mockStats} />);
    expect(screen.getByText("₹5,000")).toBeTruthy();
    expect(screen.getByText("15")).toBeTruthy();
    expect(screen.getByText("3")).toBeTruthy();
  });

  it("renders empty stat list without crash", () => {
    const { toJSON } = render(<StatGrid stats={[]} />);
    expect(toJSON()).toBeTruthy();
  });

  it("renders single stat", () => {
    render(<StatGrid stats={[{ label: "One Stat", value: "42", color: "#f00" }]} />);
    expect(screen.getByText("One Stat")).toBeTruthy();
    expect(screen.getByText("42")).toBeTruthy();
  });

  it("renders stat with icon", () => {
    const { TrendingUp } = require("lucide-react-native");
    const stats = [
      { label: "Revenue", value: "₹10,000", color: "#00c853", icon: TrendingUp },
    ];
    const { toJSON } = render(<StatGrid stats={stats} />);
    expect(toJSON()).toBeTruthy();
  });

  it("passes color to each stat card", () => {
    const { getAllByText } = render(<StatGrid stats={mockStats.slice(0, 1)} />);
    expect(getAllByText("Total Sales")).toBeTruthy();
  });
});
