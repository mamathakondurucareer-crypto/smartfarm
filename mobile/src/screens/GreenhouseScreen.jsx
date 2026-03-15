import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { Leaf, Thermometer, Droplets, Activity, Sun } from "lucide-react-native";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import StatGrid      from "../components/ui/StatGrid";
import Card          from "../components/ui/Card";
import SectionHeader from "../components/ui/SectionHeader";
import Badge         from "../components/ui/Badge";
import ProgressBar   from "../components/ui/ProgressBar";
import { colors, spacing, radius, fontSize } from "../config/theme";
import useFarmStore  from "../store/useFarmStore";

const STAGE_COLORS = {
  Harvesting: colors.primary,
  Fruiting:   colors.accent,
  Flowering:  colors.info,
  Vegetative: colors.crop,
};

export default function GreenhouseScreen() {
  const farm = useFarmStore((s) => s.farm);
  const s    = farm.sensors;

  const envStats = [
    { Icon: Thermometer, label: "GH Temperature", value: s.ghTemp,       unit: "°C",   color: s.ghTemp > 36 ? colors.danger : colors.crop },
    { Icon: Droplets,    label: "GH Humidity",    value: s.ghHumidity,   unit: "%",    color: colors.water },
    { Icon: Activity,    label: "CO₂ Level",      value: s.ghCO2,        unit: "ppm",  color: colors.crop },
    { Icon: Sun,         label: "Light (PAR)",    value: s.ghLight,      unit: "µmol", color: colors.solar },
    { Icon: Droplets,    label: "Soil Moisture",  value: s.soilMoisture, unit: "%",    color: colors.water },
    { Icon: Thermometer, label: "Soil Temp",      value: s.soilTemp,     unit: "°C",   color: colors.poultry },
  ];

  return (
    <ScreenWrapper title="Greenhouse">
      <StatGrid stats={envStats} />

      <View style={styles.gap} />

      <Card>
        <SectionHeader Icon={Leaf} title="Crop Status" color={colors.crop} />
        {farm.greenhouse.map((crop) => (
          <View key={crop.id} style={styles.cropCard}>
            <View style={styles.cropHeader}>
              <Text style={styles.cropName}>{crop.crop}</Text>
              <Badge label={crop.stage} color={STAGE_COLORS[crop.stage] ?? colors.info} />
            </View>

            <View style={styles.cropMeta}>
              <Text style={styles.metaText}>Day {crop.daysPlanted}</Text>
              <Text style={[styles.healthText, { color: healthColor(crop.health) }]}>
                Health: {crop.health}%
              </Text>
            </View>

            <Text style={styles.yieldText}>
              Yield: {crop.yieldKg.toLocaleString()} / {crop.targetKg.toLocaleString()} kg
            </Text>
            <View style={styles.progressWrap}>
              <ProgressBar value={crop.yieldKg} max={crop.targetKg} color={colors.crop} />
            </View>
          </View>
        ))}
      </Card>
    </ScreenWrapper>
  );
}

function healthColor(pct) {
  if (pct > 90) return colors.primary;
  if (pct > 80) return colors.accent;
  return colors.danger;
}

const styles = StyleSheet.create({
  gap:          { height: spacing.lg },
  cropCard:     { backgroundColor: colors.bg, borderRadius: radius.lg, padding: spacing.md, marginBottom: spacing.sm, borderWidth: 1, borderColor: colors.border },
  cropHeader:   { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: spacing.sm },
  cropName:     { fontSize: fontSize.lg, fontWeight: "700", color: colors.text },
  cropMeta:     { flexDirection: "row", justifyContent: "space-between", marginBottom: spacing.xs },
  metaText:     { fontSize: fontSize.md, color: colors.textDim },
  healthText:   { fontSize: fontSize.md, fontWeight: "600" },
  yieldText:    { fontSize: fontSize.sm, color: colors.textDim, marginBottom: spacing.xs },
  progressWrap: { marginTop: 2 },
});
