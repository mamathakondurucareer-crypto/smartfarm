import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { Sprout, Thermometer, Droplets, Activity } from "lucide-react-native";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import StatGrid      from "../components/ui/StatGrid";
import Card          from "../components/ui/Card";
import SectionHeader from "../components/ui/SectionHeader";
import Badge         from "../components/ui/Badge";
import { colors, spacing, radius, fontSize } from "../config/theme";
import useFarmStore  from "../store/useFarmStore";

export default function VerticalFarmScreen() {
  const farm = useFarmStore((s) => s.farm);
  const s    = farm.sensors;

  const envStats = [
    { Icon: Thermometer, label: "VF Temp",      value: s.vfTemp,        unit: "°C",  color: colors.verticalFarm },
    { Icon: Droplets,    label: "VF Humidity",  value: s.vfHumidity,    unit: "%",   color: colors.water },
    { Icon: Activity,    label: "Nutrient EC",  value: s.vfNutrientEC,  unit: "mS",  color: colors.primary },
    { Icon: Activity,    label: "Solution pH",  value: s.vfPH,                       color: colors.accent },
  ];

  return (
    <ScreenWrapper title="Vertical Farm">
      <StatGrid stats={envStats} />

      <View style={styles.gap} />

      <Card>
        <SectionHeader Icon={Sprout} title="Vertical Farm Tiers" color={colors.verticalFarm} />
        {farm.verticalFarm.map((tier) => (
          <View key={tier.crop} style={styles.tierCard}>
            <View style={styles.tierHeader}>
              <Text style={styles.tierCrop}>{tier.crop}</Text>
              <Badge label={`Tier ${tier.tier}`} color={colors.verticalFarm} />
            </View>
            <View style={styles.tierGrid}>
              <MetaItem label="Cycle Day"   value={`Day ${tier.cycleDay}`} />
              <MetaItem label="Health"      value={`${tier.health}%`} valueColor={colors.primary} />
              <MetaItem label="Batch"       value={`${tier.batchKg} kg`} />
              <MetaItem label="Cycles Left" value={tier.cyclesLeft} />
            </View>
          </View>
        ))}
      </Card>
    </ScreenWrapper>
  );
}

function MetaItem({ label, value, valueColor }) {
  return (
    <View style={styles.metaItem}>
      <Text style={styles.metaLabel}>{label}</Text>
      <Text style={[styles.metaValue, valueColor ? { color: valueColor, fontWeight: "600" } : null]}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  gap:        { height: spacing.lg },
  tierCard:   { backgroundColor: colors.bg, borderRadius: radius.lg, padding: spacing.md, marginBottom: spacing.sm, borderWidth: 1, borderColor: colors.border },
  tierHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: spacing.sm },
  tierCrop:   { fontSize: fontSize.lg, fontWeight: "700", color: colors.text },
  tierGrid:   { flexDirection: "row", flexWrap: "wrap", gap: spacing.sm },
  metaItem:   { width: "47%" },
  metaLabel:  { fontSize: fontSize.xs, color: colors.textMuted },
  metaValue:  { fontSize: fontSize.sm, color: colors.textDim, marginTop: 1 },
});
