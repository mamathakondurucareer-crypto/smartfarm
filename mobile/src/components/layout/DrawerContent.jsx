/**
 * Custom drawer content — shown as a permanent sidebar on tablet/desktop
 * and as a slide-in drawer on mobile.
 */
import React from "react";
import { View, Text, TouchableOpacity, ScrollView, StyleSheet } from "react-native";
import { DrawerContentScrollView } from "@react-navigation/drawer";
import { Wifi, WifiOff } from "lucide-react-native";
import { colors, spacing, radius, fontSize } from "../../config/theme";
import { SCREENS } from "../../config/navigation";
import useFarmStore from "../../store/useFarmStore";

export default function DrawerContent(props) {
  const { state, navigation } = props;
  const activeRoute   = state.routes[state.index]?.name;
  const simRunning    = useFarmStore((s) => s.simRunning);
  const toggleSim     = useFarmStore((s) => s.toggleSimulation);

  return (
    <View style={styles.container}>
      {/* Brand header */}
      <View style={styles.header}>
        <Text style={styles.brand}>🌿 SmartFarm OS</Text>
        <Text style={styles.location}>Nellore, AP</Text>
      </View>

      {/* Navigation items */}
      <DrawerContentScrollView {...props} style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {SCREENS.map(({ name, label, Icon, color }) => {
          const isActive = activeRoute === name;
          return (
            <TouchableOpacity
              key={name}
              onPress={() => navigation.navigate(name)}
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
      </DrawerContentScrollView>

      {/* Simulation toggle */}
      <TouchableOpacity
        onPress={toggleSim}
        style={[styles.simBtn, simRunning && { borderColor: colors.primary, backgroundColor: colors.primary + "15" }]}
        activeOpacity={0.8}
      >
        {simRunning
          ? <Wifi  size={14} color={colors.primary} />
          : <WifiOff size={14} color={colors.textDim} />}
        <Text style={[styles.simLabel, { color: simRunning ? colors.primary : colors.textDim }]}>
          {simRunning ? "● LIVE" : "Simulate"}
        </Text>
      </TouchableOpacity>
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
  simBtn: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    margin: spacing.md,
    padding: spacing.sm,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  simLabel: {
    fontSize: fontSize.sm,
    fontWeight: "600",
  },
});
