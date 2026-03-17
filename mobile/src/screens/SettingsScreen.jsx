/**
 * Settings — module feature toggles.
 * Admin and Manager roles can enable/disable any screen module.
 * Dashboard is always enabled and cannot be toggled.
 */
import React from "react";
import { View, Text, TouchableOpacity, ScrollView, Switch } from "react-native";
import { Settings } from "lucide-react-native";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import Card from "../components/ui/Card";
import SectionHeader from "../components/ui/SectionHeader";
import { colors, spacing, radius, fontSize } from "../config/theme";
import useFarmStore from "../store/useFarmStore";
import useAuthStore from "../store/useAuthStore";
import { SCREENS } from "../config/navigation";
import { styles } from "./SettingsScreen.styles";
import { commonStyles as cs } from "../styles/common";

const CATEGORIES = [
  { label: "Farm Operations", names: ["Aquaculture", "Greenhouse", "VerticalFarm", "Poultry", "Water", "Energy", "Automation", "Nursery"] },
  { label: "Stock & Supply Chain", names: ["StockProduced", "StockSales", "Packing", "Scanner"] },
  { label: "Store & Retail", names: ["Store", "POS", "Logistics"] },
  { label: "Finance & Markets", names: ["Market", "Financial", "Reports"] },
  { label: "Admin & AI", names: ["AI", "ServiceRequests", "ActivityLog", "Users"] },
];

export default function SettingsScreen() {
  const enabledModules = useFarmStore((s) => s.farm.enabledModules ?? {});
  const toggleModule   = useFarmStore((s) => s.toggleModule);
  const user           = useAuthStore((s) => s.user);
  const canEdit        = ["ADMIN", "MANAGER"].includes((user?.role ?? "").toUpperCase());

  const screenMap = Object.fromEntries(SCREENS.map((s) => [s.name, s]));

  return (
    <ScreenWrapper title="Settings">
      <Card>
        <SectionHeader Icon={Settings} title="Module Toggles" color={colors.primary} />
        <Text style={styles.hint}>
          {canEdit ? "Enable or disable feature modules from the navigation." : "Only Admin and Manager can change module settings."}
        </Text>
      </Card>

      <View style={cs.gap} />

      <ScrollView showsVerticalScrollIndicator={false}>
        {CATEGORIES.map((cat) => (
          <View key={cat.label} style={styles.section}>
            <Text style={styles.catLabel}>{cat.label}</Text>
            <Card>
              {cat.names.map((name, idx) => {
                const screen  = screenMap[name];
                if (!screen) return null;
                const enabled = enabledModules[name] !== false;
                const { Icon, label, color } = screen;
                return (
                  <View
                    key={name}
                    style={[cs.row, idx < cat.names.length - 1 && styles.rowBorder]}
                  >
                    <View style={styles.rowLeft}>
                      <View style={[styles.iconBox, { backgroundColor: color + "20" }]}>
                        <Icon size={15} color={color} />
                      </View>
                      <Text style={[styles.rowLabel, !enabled && styles.rowLabelOff]}>{label}</Text>
                    </View>
                    <Switch
                      value={enabled}
                      onValueChange={() => canEdit && toggleModule(name)}
                      disabled={!canEdit}
                      trackColor={{ false: colors.border, true: color + "80" }}
                      thumbColor={enabled ? color : colors.textMuted}
                    />
                  </View>
                );
              })}
            </Card>
            <View style={cs.gap} />
          </View>
        ))}
      </ScrollView>
    </ScreenWrapper>
  );
}

