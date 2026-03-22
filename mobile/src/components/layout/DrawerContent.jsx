/**
 * Custom drawer content — permanent sidebar on tablet/desktop,
 * slide-in drawer on mobile.
 * Screens are grouped by department/function (section) with
 * collapsible section headers. Filters by the logged-in user's role.
 */
import React, { useState, useMemo } from "react";
import { View, Text, TouchableOpacity, ScrollView, StyleSheet } from "react-native";
import { Wifi, WifiOff, LogOut, User, ChevronDown, ChevronRight } from "lucide-react-native";
import { colors, spacing, radius, fontSize } from "../../config/theme";
import { SCREENS, SECTIONS } from "../../config/navigation";
import { canAccessScreen } from "../../config/permissions";
import useFarmStore  from "../../store/useFarmStore";
import useAuthStore  from "../../store/useAuthStore";
import { useNavigation } from "../../context/NavigationContext";

export default function DrawerContent() {
  const { activeScreen, navigate } = useNavigation();
  const simRunning     = useFarmStore((s) => s.simRunning);
  const toggleSim      = useFarmStore((s) => s.toggleSimulation);
  const user           = useAuthStore((s) => s.user);
  const logout         = useAuthStore((s) => s.logout);
  const userRole       = (user?.role ?? "VIEWER").toUpperCase();
  const enabledModules = useFarmStore((s) => s.farm.enabledModules ?? {});

  // All sections start expanded
  const [collapsed, setCollapsed] = useState({});
  const toggleSection = (key) =>
    setCollapsed((prev) => ({ ...prev, [key]: !prev[key] }));

  // Filter screens by role + module toggles, then group by section
  const grouped = useMemo(() => {
    const visible = SCREENS.filter(
      (s) => canAccessScreen(s.name, userRole) && enabledModules[s.name] !== false
    );
    const bySection = {};
    for (const screen of visible) {
      const key = screen.section ?? "admin";
      if (!bySection[key]) bySection[key] = [];
      bySection[key].push(screen);
    }
    return bySection;
  }, [userRole, enabledModules]);

  return (
    <View style={styles.container}>
      {/* Brand header */}
      <View style={styles.header}>
        <Text style={styles.brand}>🌿 SmartFarm OS</Text>
        <Text style={styles.location}>Nellore, AP</Text>
      </View>

      {/* Logged-in user */}
      {user && (
        <View style={styles.userRow}>
          <User size={14} color={colors.textDim} />
          <View style={styles.userInfo}>
            <Text style={styles.userName}>{user.full_name}</Text>
            <Text style={styles.userRole}>{userRole}</Text>
          </View>
        </View>
      )}

      {/* Grouped navigation */}
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {SECTIONS.map(({ key, label }) => {
          const screens = grouped[key];
          if (!screens || screens.length === 0) return null;
          const isCollapsed = !!collapsed[key];

          return (
            <View key={key}>
              {/* Section header */}
              <TouchableOpacity
                onPress={() => toggleSection(key)}
                style={styles.sectionHeader}
                activeOpacity={0.7}
              >
                <Text style={styles.sectionLabel}>{label.toUpperCase()}</Text>
                {isCollapsed
                  ? <ChevronRight size={12} color={colors.textMuted} />
                  : <ChevronDown  size={12} color={colors.textMuted} />}
              </TouchableOpacity>

              {/* Section items */}
              {!isCollapsed && screens.map(({ name, label: itemLabel, Icon, color }) => {
                const isActive = activeScreen === name;
                return (
                  <TouchableOpacity
                    key={name}
                    onPress={() => navigate(name)}
                    style={[styles.navItem, isActive && { backgroundColor: color + "20" }]}
                    activeOpacity={0.7}
                  >
                    <Icon size={16} color={isActive ? color : colors.textDim} />
                    <Text style={[styles.navLabel, { color: isActive ? color : colors.textDim }]}>
                      {itemLabel}
                    </Text>
                  </TouchableOpacity>
                );
              })}
            </View>
          );
        })}
      </ScrollView>

      {/* Bottom controls */}
      <View style={styles.bottomSection}>
        <TouchableOpacity
          onPress={toggleSim}
          style={[styles.simBtn, simRunning && { borderColor: colors.primary, backgroundColor: colors.primary + "15" }]}
          activeOpacity={0.8}
        >
          {simRunning
            ? <Wifi    size={14} color={colors.primary} />
            : <WifiOff size={14} color={colors.textDim} />}
          <Text style={[styles.simLabel, { color: simRunning ? colors.primary : colors.textDim }]}>
            {simRunning ? "● LIVE" : "Simulate"}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity onPress={logout} style={styles.logoutBtn} activeOpacity={0.8}>
          <LogOut size={14} color={colors.danger} />
          <Text style={styles.logoutLabel}>Sign Out</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.card,
    borderRightWidth: 1,
    borderRightColor: colors.border,
  },
  header: {
    padding: spacing.lg,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  brand: {
    fontSize: fontSize.lg,
    fontWeight: "700",
    color: colors.primary,
  },
  location: {
    fontSize: fontSize.xs,
    color: colors.textMuted,
    marginTop: 2,
  },
  userRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    padding: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    backgroundColor: colors.bg,
  },
  userInfo:  { flex: 1 },
  userName:  { fontSize: fontSize.md, color: colors.text, fontWeight: "600" },
  userRole:  { fontSize: fontSize.xs, color: colors.textMuted },
  scrollView: {
    flex: 1,
    paddingVertical: spacing.xs,
  },
  sectionHeader: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: spacing.md,
    paddingVertical: 6,
    marginTop: spacing.xs,
  },
  sectionLabel: {
    fontSize: 10,
    fontWeight: "700",
    color: colors.textMuted,
    letterSpacing: 0.8,
  },
  navItem: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    paddingHorizontal: spacing.md,
    paddingVertical: 9,
    marginHorizontal: spacing.sm,
    marginVertical: 1,
    borderRadius: radius.md,
  },
  navLabel: {
    fontSize: fontSize.md,
    fontWeight: "400",
  },
  bottomSection: {
    borderTopWidth: 1,
    borderTopColor: colors.border,
    padding: spacing.sm,
    gap: spacing.xs,
  },
  simBtn: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    padding: spacing.sm,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  simLabel: {
    fontSize: fontSize.sm,
    fontWeight: "600",
  },
  logoutBtn: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    padding: spacing.sm,
    borderRadius: radius.md,
  },
  logoutLabel: {
    fontSize: fontSize.sm,
    color: colors.danger,
    fontWeight: "600",
  },
});
