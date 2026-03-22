/**
 * Responsive breakpoint hook.
 *
 * Returns layout descriptors based on current window width so
 * components can adapt without media queries.
 *
 * Breakpoints:
 *   mobile        — < 768 px    → overlay drawer, bottom tab bar, 2 cols
 *   tablet/iPad   — 768–1023 px → permanent sidebar (200 px), 3 cols
 *   desktop       — 1024–1439px → permanent sidebar (240 px), 4 cols
 *   large desktop — ≥ 1440 px   → sidebar + max-width content container
 */
import { useWindowDimensions } from "react-native";

const BP = { tablet: 768, desktop: 1024, large: 1440 };

export function useResponsive() {
  const { width, height } = useWindowDimensions();

  const isMobile       = width < BP.tablet;
  const isTablet       = width >= BP.tablet && width < BP.desktop;
  const isDesktop      = width >= BP.desktop;
  const isLargeDesktop = width >= BP.large;

  /** Number of columns for stat/metric grids */
  const statColumns = isDesktop ? 4 : isTablet ? 3 : 2;

  /** Number of columns for content cards */
  const cardColumns = isDesktop ? 2 : 1;

  /** Drawer is always visible on tablet and above */
  const showPermanentDrawer = !isMobile;

  /** Bottom tab bar is only shown on mobile */
  const bottomTabVisible = isMobile;

  /** Sidebar width — wider on desktop for breathing room */
  const drawerWidth = isDesktop ? 240 : 200;

  /** Horizontal padding for screen content */
  const screenPadding = isDesktop ? 32 : isTablet ? 24 : 16;

  /** App bar height — taller on desktop for hierarchy */
  const headerHeight = isDesktop ? 62 : 54;

  /**
   * Maximum content width — constrains content on very wide screens
   * so text lines stay readable. undefined on mobile/tablet (full width).
   */
  const contentMaxWidth = isLargeDesktop ? 1400 : isDesktop ? 1200 : undefined;

  /**
   * Correct pixel width for chart components — deducts drawer sidebar,
   * screen padding (both sides), and card inner padding (spacing.lg × 2 = 32).
   */
  const chartWidth = width
    - (showPermanentDrawer ? drawerWidth : 0)
    - screenPadding * 2
    - 32;

  /** Maximum width for modal dialogs on larger screens */
  const modalMaxWidth = isDesktop ? 600 : isTablet ? 520 : undefined;

  return {
    width,
    height,
    isMobile,
    isTablet,
    isDesktop,
    isLargeDesktop,
    statColumns,
    cardColumns,
    showPermanentDrawer,
    bottomTabVisible,
    drawerWidth,
    screenPadding,
    headerHeight,
    contentMaxWidth,
    chartWidth,
    modalMaxWidth,
  };
}
