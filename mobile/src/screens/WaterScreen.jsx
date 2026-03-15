import React from "react";
import { View, Text, ScrollView, StyleSheet } from "react-native";
import { Droplets, Database, Sun, Fish, Sprout, RefreshCw, CloudRain, Activity, ChevronRight, BarChart3 } from "lucide-react-native";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import StatGrid      from "../components/ui/StatGrid";
import Card          from "../components/ui/Card";
import SectionHeader from "../components/ui/SectionHeader";
import BarChartCard  from "../components/charts/BarChartCard";
import { colors, spacing, radius, fontSize } from "../config/theme";
import useFarmStore  from "../store/useFarmStore";

const WATER_BUDGET = [
  { label: "Fish Ponds",   litres: 25000 },
  { label: "Greenhouse",   litres: 5000 },
  { label: "Field Crops",  litres: 8000 },
  { label: "Nursery",      litres: 2000 },
  { label: "Poultry/Duck", litres: 1500 },
  { label: "Vertical Farm",litres: 500 },
  { label: "Packhouse",    litres: 1000 },
  { label: "Misc",         litres: 500 },
];

const FLOW_STAGES = [
  { label: "Reservoir",     Icon: Database, color: colors.water },
  { label: "Solar Pump",    Icon: Sun,      color: colors.solar },
  { label: "Header Tank",   Icon: Droplets, color: colors.info },
  { label: "Gravity Drip",  Icon: Sprout,   color: colors.crop },
  { label: "Fish Ponds",    Icon: Fish,     color: colors.fish },
  { label: "Collection",    Icon: RefreshCw,color: colors.primary },
];

export default function WaterScreen() {
  const farm = useFarmStore((s) => s.farm);
  const s    = farm.sensors;

  const summaryStats = [
    { Icon: Database, label: "Reservoir",     value: `${s.reservoirLevel}%`, color: colors.water, sub: "~7.8M litres" },
    { Icon: Droplets, label: "Header Tank",   value: `${s.headerTankLevel}%`, color: colors.info, sub: "30,000L cap" },
    { Icon: CloudRain,label: "Rainfall",      value: s.rainfall, unit: "mm", color: colors.water },
    { Icon: Activity, label: "Daily Usage",   value: "43,500",   unit: "L",  color: colors.textDim },
  ];

  return (
    <ScreenWrapper title="Water System">
      <StatGrid stats={summaryStats} />

      <View style={styles.gap} />

      {/* Closed loop flow diagram */}
      <Card>
        <SectionHeader Icon={Droplets} title="Closed Loop Water Flow" color={colors.water} />
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          <View style={styles.flowRow}>
            {FLOW_STAGES.map((stage, i) => (
              <View key={i} style={styles.flowItem}>
                <View style={[styles.flowNode, { backgroundColor: stage.color + "18", borderColor: stage.color + "40" }]}>
                  <stage.Icon size={20} color={stage.color} />
                  <Text style={styles.flowLabel}>{stage.label}</Text>
                </View>
                {i < FLOW_STAGES.length - 1 && <ChevronRight size={16} color={colors.textMuted} />}
              </View>
            ))}
            <ChevronRight size={16} color={colors.textMuted} />
            <View style={styles.recycleLabel}>
              <Text style={[styles.recycleTxt, { color: colors.water }]}>↺ Reservoir</Text>
            </View>
          </View>
        </ScrollView>
      </Card>

      <View style={styles.gap} />

      <BarChartCard
        Icon={BarChart3}
        title="Daily Water Budget"
        color={colors.water}
        labels={WATER_BUDGET.map((b) => b.label.split("/")[0])}
        data={WATER_BUDGET.map((b) => b.litres)}
        yLabel="L"
        height={220}
      />
    </ScreenWrapper>
  );
}

const styles = StyleSheet.create({
  gap:          { height: spacing.lg },
  flowRow:      { flexDirection: "row", alignItems: "center", gap: spacing.xs, paddingVertical: spacing.sm },
  flowItem:     { flexDirection: "row", alignItems: "center", gap: spacing.xs },
  flowNode:     { alignItems: "center", padding: spacing.md, borderRadius: radius.lg, borderWidth: 1, minWidth: 90 },
  flowLabel:    { fontSize: fontSize.xs, fontWeight: "700", color: colors.text, marginTop: 4, textAlign: "center" },
  recycleLabel: { paddingHorizontal: spacing.sm, paddingVertical: spacing.xs, borderWidth: 1, borderStyle: "dashed", borderColor: colors.water, borderRadius: radius.sm },
  recycleTxt:   { fontSize: fontSize.sm, fontWeight: "600" },
});
