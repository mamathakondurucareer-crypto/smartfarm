/**
 * Design tokens — single source of truth for all colors, spacing,
 * and typography across the app.
 */

export const colors = {
  // Backgrounds
  bg:       "#0B1A14",
  card:     "#122A1E",
  border:   "#1E4D35",

  // Brand
  primary:     "#2ECC71",
  primaryDim:  "#27AE60",
  accent:      "#F1C40F",

  // Status
  danger:  "#E74C3C",
  warn:    "#F39C12",
  info:    "#3498DB",
  success: "#2ECC71",

  // Text
  text:      "#E8F5E9",
  textDim:   "#8FAF9A",
  textMuted: "#5A7A66",
  white:     "#FFFFFF",

  // Domain colors
  water:       "#2980B9",
  solar:       "#F39C12",
  fish:        "#1ABC9C",
  crop:        "#27AE60",
  poultry:     "#E67E22",
  market:      "#9B59B6",
  verticalFarm:"#8E44AD",
  ai:          "#00BCD4",

  // Store / retail
  store:       "#E91E63",
  pos:         "#FF5722",
  logistics:   "#607D8B",
  packing:     "#FF9800",
  scanner:     "#00BFA5",
  reports:     "#7C4DFF",
  service:     "#FF6D00",
};

export const spacing = {
  xs:  4,
  sm:  8,
  md:  12,
  lg:  16,
  xl:  20,
  xxl: 24,
};

export const radius = {
  sm: 6,
  md: 8,
  lg: 10,
  xl: 12,
};

export const fontSize = {
  xs:   10,
  sm:   11,
  md:   12,
  base: 13,
  lg:   14,
  xl:   16,
  xxl:  18,
  h1:   22,
};

/** Ordered chart palette for multi-series charts */
export const chartColors = [
  colors.fish, colors.crop, colors.primary, colors.accent,
  colors.poultry, colors.info, colors.market, colors.danger,
];
