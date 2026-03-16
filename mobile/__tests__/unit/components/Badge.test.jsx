/**
 * Unit tests for Badge component.
 */

import React from "react";
import { render, screen } from "@testing-library/react-native";
import Badge from "../../../src/components/ui/Badge";

describe("Badge", () => {
  it("renders label text", () => {
    render(<Badge label="completed" color="#00c853" />);
    expect(screen.getByText("completed")).toBeTruthy();
  });

  it("renders with custom color", () => {
    const { getByText } = render(<Badge label="low" color="#ff6b35" />);
    const text = getByText("low");
    expect(text.props.style).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ color: "#ff6b35" }),
      ])
    );
  });

  it("uses a default color when none is provided", () => {
    const { getByText } = render(<Badge label="default" />);
    const text = getByText("default");
    // Should render without throwing
    expect(text).toBeTruthy();
  });

  it("renders empty string label without crashing", () => {
    const { toJSON } = render(<Badge label="" color="#aaa" />);
    expect(toJSON()).toBeTruthy();
  });

  it("renders long label text", () => {
    const longLabel = "store_replenishment_order";
    render(<Badge label={longLabel} color="#333" />);
    expect(screen.getByText(longLabel)).toBeTruthy();
  });

  it("background color includes alpha from color prop", () => {
    const { UNSAFE_getByType } = render(<Badge label="test" color="#00c853" />);
    const view = UNSAFE_getByType(require("react-native").View);
    const bg = view.props.style[1]?.backgroundColor;
    // Badge creates background as color + "22"
    expect(bg).toBe("#00c85322");
  });
});
