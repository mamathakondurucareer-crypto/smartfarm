/**
 * Wraps every screen with:
 *  - A responsive top header (compact on mobile, prominent on desktop)
 *  - SafeAreaView + ScrollView with responsive padding
 *  - Content max-width centering on large desktop screens
 *  - Alert dropdown overlay
 *  - Extra bottom padding on mobile to clear the bottom tab bar
 */
import React, { useState } from "react";
import {
  View, Text, ScrollView, TouchableOpacity,
  StyleSheet, StatusBar, Platform,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Bell, Menu } from "lucide-react-native";
import { colors, spacing, fontSize, radius } from "../../config/theme";
import { useResponsive } from "../../hooks/useResponsive";
import useFarmStore from "../../store/useFarmStore";
import AlertDot from "../ui/AlertDot";
import { useNavigation } from "../../context/NavigationContext";

// Extra clearance above the mobile bottom tab bar (58 px bar + buffer)
const MOBILE_BOTTOM_CLEARANCE = 72;

export default function ScreenWrapper({ title, children }) {
  const [alertsOpen, setAlertsOpen] = useState(false);
  const {
    screenPadding,
    showPermanentDrawer,
    bottomTabVisible,
    contentMaxWidth,
    isDesktop,
    isTablet,
  } = useResponsive();
  const { toggleDrawer } = useNavigation();
  const farm        = useFarmStore((s) => s.farm);
  const hasCritical = farm.alerts.some((a) => a.type === "danger");
  const updatedAt   = new Date(farm.lastUpdated).toLocaleTimeString();

  const paddingBottom = bottomTabVisible
    ? MOBILE_BOTTOM_CLEARANCE
    : spacing.xxl * 2;

  return (
    <SafeAreaView style={styles.safe} edges={["top", "right", "left"]}>
      <StatusBar barStyle="light-content" backgroundColor={colors.card} />

      {/* ── Header ── */}
      <View style={[styles.header, isDesktop && styles.headerDesktop]}>
        <View style={styles.headerLeft}>
          {/* Hamburger — only on mobile where drawer is hidden */}
          {!showPermanentDrawer && (
            <TouchableOpacity
              onPress={toggleDrawer}
              style={styles.menuBtn}
              activeOpacity={0.7}
              hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
            >
              <Menu size={22} color={colors.textDim} />
            </TouchableOpacity>
          )}

          <View>
            <Text style={[styles.pageTitle, isDesktop && styles.pageTitleDesktop]}>
              {title}
            </Text>
            {/* Subtitle hidden on very small mobiles (extra noise), shown on tablet+ and desktop */}
            {(isTablet || isDesktop) && (
              <Text style={styles.subtitle}>Nellore District, AP · {updatedAt}</Text>
            )}
          </View>
        </View>

        <View style={styles.headerRight}>
          {/* Last updated — shown on desktop in the header */}
          {isDesktop && (
            <Text style={styles.updatedAt}>Updated {updatedAt}</Text>
          )}

          <TouchableOpacity
            onPress={() => setAlertsOpen((o) => !o)}
            style={[styles.bellBtn, hasCritical && styles.bellBtnAlert]}
            activeOpacity={0.7}
            hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
          >
            <Bell size={isDesktop ? 22 : 20} color={hasCritical ? colors.danger : colors.textDim} />
            {hasCritical && <View style={styles.bellDot} />}
          </TouchableOpacity>
        </View>
      </View>

      {/* ── Alert dropdown ── */}
      {alertsOpen && (
        <View style={[styles.alertPanel, isDesktop && styles.alertPanelDesktop]}>
          <Text style={styles.alertPanelTitle}>
            Alerts ({farm.alerts.length})
          </Text>
          {farm.alerts.slice(0, 8).map((a) => (
            <View key={a.id} style={styles.alertRow}>
              <AlertDot type={a.type} />
              <View style={styles.alertBody}>
                <Text style={styles.alertMsg}>{a.msg}</Text>
                <Text style={styles.alertMeta}>{a.system} · {a.time}</Text>
              </View>
            </View>
          ))}
        </View>
      )}

      {/* ── Screen content ── */}
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={[
          styles.scrollContent,
          { padding: screenPadding, paddingBottom },
          // Centre content on large desktop (align-self trick)
          contentMaxWidth && { alignItems: "stretch" },
        ]}
        onScrollBeginDrag={() => setAlertsOpen(false)}
        showsVerticalScrollIndicator={false}
      >
        {/*
         * On desktop, constrain content width so lines stay readable
         * on ultra-wide monitors. alignSelf + maxWidth + width centres
         * the block while still filling narrower screens.
         */}
        <View
          style={
            contentMaxWidth
              ? { maxWidth: contentMaxWidth, width: "100%", alignSelf: "center" }
              : styles.contentFull
          }
        >
          {children}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: colors.bg,
  },

  // ── Header ────────────────────────────────────────────────────────
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    backgroundColor: colors.card,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.md,
    minHeight: 54,
  },
  headerDesktop: {
    paddingVertical: spacing.lg,
    paddingHorizontal: spacing.xxl,
    minHeight: 62,
  },
  headerLeft: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    flex: 1,
    minWidth: 0,
  },
  headerRight: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.md,
    flexShrink: 0,
  },
  menuBtn: {
    padding: spacing.xs,
    marginRight: spacing.xs,
    borderRadius: radius.sm,
  },
  pageTitle: {
    fontSize: fontSize.xl,
    fontWeight: "700",
    color: colors.text,
  },
  pageTitleDesktop: {
    fontSize: fontSize.xxl,
    fontWeight: "700",
  },
  subtitle: {
    fontSize: fontSize.sm,
    color: colors.textMuted,
    marginTop: 1,
  },
  updatedAt: {
    fontSize: fontSize.sm,
    color: colors.textMuted,
  },
  bellBtn: {
    position: "relative",
    padding: spacing.xs,
    borderRadius: radius.sm,
  },
  bellBtnAlert: {
    backgroundColor: colors.danger + "15",
  },
  bellDot: {
    position: "absolute",
    top: spacing.xs,
    right: spacing.xs,
    width: 7,
    height: 7,
    borderRadius: 4,
    backgroundColor: colors.danger,
  },

  // ── Alert panel ───────────────────────────────────────────────────
  alertPanel: {
    position: "absolute",
    top: 54,
    right: spacing.lg,
    width: 320,
    maxHeight: 360,
    backgroundColor: colors.card,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.xl,
    zIndex: 999,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.4,
    shadowRadius: 16,
    elevation: 10,
    overflow: "hidden",
  },
  alertPanelDesktop: {
    top: 62,
    width: 380,
    maxHeight: 440,
  },
  alertPanelTitle: {
    fontSize: fontSize.base,
    fontWeight: "600",
    color: colors.text,
    padding: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  alertRow: {
    flexDirection: "row",
    gap: spacing.sm,
    padding: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border + "40",
  },
  alertBody: { flex: 1 },
  alertMsg:  { fontSize: fontSize.md, color: colors.text },
  alertMeta: { fontSize: fontSize.xs, color: colors.textMuted, marginTop: 2 },

  // ── Content area ──────────────────────────────────────────────────
  scroll:      { flex: 1 },
  scrollContent: {},
  contentFull: { flex: 1 },
});
