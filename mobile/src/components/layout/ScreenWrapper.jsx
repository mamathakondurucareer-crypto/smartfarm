/**
 * Wraps every screen with:
 *  - A consistent top header (title, location, timestamp, alerts bell)
 *  - SafeAreaView + ScrollView with responsive padding
 *  - Alert dropdown overlay
 */
import React, { useState } from "react";
import {
  View, Text, ScrollView, TouchableOpacity,
  StyleSheet, StatusBar, Platform,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Bell } from "lucide-react-native";
import { colors, spacing, fontSize, radius } from "../../config/theme";
import { useResponsive } from "../../hooks/useResponsive";
import useFarmStore from "../../store/useFarmStore";
import AlertDot from "../ui/AlertDot";

export default function ScreenWrapper({ title, children }) {
  const [alertsOpen, setAlertsOpen] = useState(false);
  const { screenPadding } = useResponsive();
  const farm = useFarmStore((s) => s.farm);
  const hasCritical = farm.alerts.some((a) => a.type === "danger");
  const updatedAt   = new Date(farm.lastUpdated).toLocaleTimeString();

  return (
    <SafeAreaView style={styles.safe} edges={["top", "right", "left"]}>
      <StatusBar barStyle="light-content" backgroundColor={colors.card} />

      {/* ── Header ── */}
      <View style={styles.header}>
        <View>
          <Text style={styles.pageTitle}>{title}</Text>
          <Text style={styles.subtitle}>Nellore District, AP • {updatedAt}</Text>
        </View>

        <TouchableOpacity onPress={() => setAlertsOpen((o) => !o)} style={styles.bellBtn} activeOpacity={0.7}>
          <Bell size={20} color={colors.textDim} />
          {hasCritical && <View style={styles.bellDot} />}
        </TouchableOpacity>
      </View>

      {/* ── Alert dropdown ── */}
      {alertsOpen && (
        <View style={styles.alertPanel}>
          <Text style={styles.alertPanelTitle}>Alerts ({farm.alerts.length})</Text>
          {farm.alerts.slice(0, 8).map((a) => (
            <View key={a.id} style={styles.alertRow}>
              <AlertDot type={a.type} />
              <View style={styles.alertBody}>
                <Text style={styles.alertMsg}>{a.msg}</Text>
                <Text style={styles.alertMeta}>{a.system} • {a.time}</Text>
              </View>
            </View>
          ))}
        </View>
      )}

      {/* ── Screen content ── */}
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={{ padding: screenPadding, paddingBottom: spacing.xxl * 2 }}
        onScrollBeginDrag={() => setAlertsOpen(false)}
        showsVerticalScrollIndicator={false}
      >
        {children}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: colors.bg,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    backgroundColor: colors.card,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.md,
  },
  pageTitle: {
    fontSize: fontSize.xl,
    fontWeight: "700",
    color: colors.text,
  },
  subtitle: {
    fontSize: fontSize.sm,
    color: colors.textMuted,
    marginTop: 1,
  },
  bellBtn: {
    position: "relative",
    padding: spacing.xs,
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
  alertPanel: {
    position: "absolute",
    top: Platform.OS === "web" ? 56 : 90,
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
  scroll: { flex: 1 },
});
