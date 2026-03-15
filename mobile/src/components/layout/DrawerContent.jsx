/**
 * Custom drawer content — permanent sidebar on tablet/desktop,
 * slide-in drawer on mobile.
 * Filters nav items by the logged-in user's role.
 */
import React from "react";
import { View, Text, TouchableOpacity, ScrollView, StyleSheet } from "react-native";
import { Wifi, WifiOff, LogOut, User } from "lucide-react-native";
import { colors, spacing, radius, fontSize } from "../../config/theme";
import { SCREENS } from "../../config/navigation";
import { canAccessScreen } from "../../config/permissions";
import useFarmStore  from "../../store/useFarmStore";
import useAuthStore  from "../../store/useAuthStore";
import { useNavigation } from "../../context/NavigationContext";

export default function DrawerContent() {
  const { activeScreen, navigate } = useNavigation();
  const simRunning = useFarmStore((s) => s.simRunning);
  const toggleSim  = useFarmStore((s) => s.toggleSimulation);
  const user       = useAuthStore((s) => s.user);
  const logout     = useAuthStore((s) => s.logout);
  const userRole   = (user?.role ?? "VIEWER").toUpperCase();

  const visibleScreens = SCREENS.filter((s) => canAccessScreen(s.name, userRole));

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

      {/* Navigation items filtered by role */}
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {visibleScreens.map(({ name, label, Icon, color }) => {
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
                {label}
              </Text>
            </TouchableOpacity>
          );
        })}
      </ScrollView>

      {/* Bottom controls */}
      <View style={styles.bottomSection}>
        {/* Simulation toggle */}
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

        {/* Logout */}
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
    paddingVertical: spacing.sm,
  },
  navItem: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    paddingHorizontal: spacing.md,
    paddingVertical: 10,
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
