/**
 * Jest global setup — mocks platform modules that can't run in Node.
 */

// Mock AsyncStorage
jest.mock("@react-native-async-storage/async-storage", () =>
  require("@react-native-async-storage/async-storage/jest/async-storage-mock")
);

// Mock lucide-react-native icons (returns a no-op component)
jest.mock("lucide-react-native", () => {
  const React = require("react");
  const MockIcon = (props) => React.createElement("View", props);
  const handler = {
    get: (_target, prop) => MockIcon,
  };
  return new Proxy({}, handler);
});

// Mock react-native-chart-kit
jest.mock("react-native-chart-kit", () => ({
  LineChart: () => null,
  BarChart: () => null,
  PieChart: () => null,
  ProgressChart: () => null,
}));

// Mock react-native-svg
jest.mock("react-native-svg", () => ({
  Svg: "Svg",
  Circle: "Circle",
  Rect: "Rect",
  Path: "Path",
  G: "G",
  Text: "Text",
}));

// Suppress console.error for known RN warnings during tests
const originalConsoleError = console.error;
console.error = (...args) => {
  if (
    typeof args[0] === "string" &&
    (args[0].includes("Warning: ReactDOM.render") ||
      args[0].includes("Warning: An update to") ||
      args[0].includes("act("))
  ) {
    return;
  }
  originalConsoleError(...args);
};
