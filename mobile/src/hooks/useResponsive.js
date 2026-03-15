/**
 * Responsive breakpoint hook.
 *
 * Returns layout descriptors based on current window width so
 * components can adapt columns, font sizes, and navigation style
 * without media queries.
 *
 * Breakpoints:
 *   mobile  — < 768 px   → bottom tab navigation, 1–2 cols
 *   tablet  — 768–1023px → side drawer, 2–3 cols
 *   desktop — ≥ 1024 px  → permanent drawer, 3–4 cols
 */
import { useWindowDimensions } from "react-native";

const BREAKPOINTS = { tablet: 768, desktop: 1024 };

export function useResponsive() {
  const { width, height } = useWindowDimensions();

  const isMobile  = width < BREAKPOINTS.tablet;
  const isTablet  = width >= BREAKPOINTS.tablet && width < BREAKPOINTS.desktop;
  const isDesktop = width >= BREAKPOINTS.desktop;

  /** Number of grid columns for stat cards */
  const statColumns = isDesktop ? 4 : isTablet ? 3 : 2;

  /** Number of grid columns for content cards */
  const cardColumns = isDesktop ? 2 : 1;

  /** Whether the drawer sidebar should be permanently visible */
  const showPermanentDrawer = !isMobile;

  /** Width of the drawer sidebar when open */
  const drawerWidth = isDesktop ? 220 : 180;

  /** Horizontal padding for screen content */
  const screenPadding = isDesktop ? 28 : isTablet ? 20 : 16;

  return {
    width,
    height,
    isMobile,
    isTablet,
    isDesktop,
    statColumns,
    cardColumns,
    showPermanentDrawer,
    drawerWidth,
    screenPadding,
  };
}
