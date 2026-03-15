import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { Sprout, Truck, Activity, Leaf } from "lucide-react-native";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import StatGrid      from "../components/ui/StatGrid";
import Card          from "../components/ui/Card";
import SectionHeader from "../components/ui/SectionHeader";
import { colors, spacing, radius, fontSize } from "../config/theme";
import useFarmStore  from "../store/useFarmStore";

export default function NurseryScreen() {
  const { nursery: n, bees } = useFarmStore((s) => s.farm);

  const stats = [
    { Icon: Sprout,   label: "Seedlings Ready",    value: `${(n.seedlingsReady / 1000).toFixed(0)}K`, color: colors.primary, sub: "of 300K capacity" },
    { Icon: Truck,    label: "Orders This Month",  value: n.ordersThisMonth, color: colors.accent },
    { Icon: Activity, label: "Capacity Used",      value: `${n.capacityUsed}%`, color: colors.info },
    { Icon: Leaf,     label: "Species Available",  value: n.species,          color: colors.crop },
  ];

  return (
    <ScreenWrapper title="Nursery & Bees">
      <StatGrid stats={stats} />

      <View style={styles.gap} />

      <Card>
        <SectionHeader Icon={Sprout} title="Seedling Nursery" color={colors.primary} />
        <InfoItem label="Monthly Capacity"  value="300,000 seedlings" />
        <InfoItem label="Current Readiness" value={n.seedlingsReady.toLocaleString()} />
        <InfoItem label="Active Species"    value={`${n.species} varieties`} />
        <InfoItem label="Revenue / Month"   value="₹5.2 Lakh" />
        <InfoItem label="Top Sellers"       value="Tomato, Chilli, Brinjal, Marigold" />
      </Card>

      <View style={styles.gap} />

      <Card>
        <SectionHeader Icon={Sprout} title="Apiculture — 20 Hives" color={colors.accent} />
        <InfoItem label="Active Hives"      value={bees.hives} />
        <InfoItem label="Forager Activity"  value={bees.activeForagers} />
        <InfoItem label="Honey Stored"      value={`${bees.honeyStored} kg`} />
        <InfoItem label="Last Inspection"   value={bees.lastInspection} />
        <InfoItem label="Pollination Boost" value="+18% greenhouse yield" />
      </Card>
    </ScreenWrapper>
  );
}

function InfoItem({ label, value }) {
  return (
    <View style={styles.row}>
      <Text style={styles.label}>{label}</Text>
      <Text style={styles.value}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  gap:   { height: spacing.lg },
  row:   { flexDirection: "row", justifyContent: "space-between", paddingVertical: 6, borderBottomWidth: 1, borderBottomColor: colors.border + "40" },
  label: { fontSize: fontSize.md, color: colors.textDim },
  value: { fontSize: fontSize.md, color: colors.text, fontWeight: "500", flexShrink: 1, textAlign: "right", marginLeft: spacing.sm },
});
