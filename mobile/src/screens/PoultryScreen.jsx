import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { Egg, Users, TrendingUp, Activity, Thermometer, AlertTriangle, Bug, Sprout } from "lucide-react-native";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import Card          from "../components/ui/Card";
import SectionHeader from "../components/ui/SectionHeader";
import StatGrid      from "../components/ui/StatGrid";
import { colors, spacing, radius, fontSize } from "../config/theme";
import useFarmStore  from "../store/useFarmStore";

export default function PoultryScreen() {
  const farm = useFarmStore((s) => s.farm);
  const { poultry: p, ducks: d, bees, sensors: s } = farm;

  const henStats = [
    { Icon: Users,         label: "Active Hens",  value: p.hens,          color: colors.poultry, compact: true },
    { Icon: Egg,           label: "Eggs Today",   value: p.eggsToday,     color: colors.accent,  compact: true, sub: `${p.eggsBroken} broken` },
    { Icon: TrendingUp,    label: "Lay Rate",     value: `${p.layRate}%`, color: colors.primary, compact: true },
    { Icon: Activity,      label: "Feed Used",    value: `${p.feedConsumed}kg`, color: colors.poultry, compact: true },
    { Icon: Thermometer,   label: "Shed Temp",    value: s.poultryTemp,   unit: "°C", color: colors.info,    compact: true },
    { Icon: AlertTriangle, label: "NH₃ Level",    value: s.poultryAmmonia, unit: "ppm", color: s.poultryAmmonia > 20 ? colors.danger : colors.primary, compact: true },
  ];

  const duckStats = [
    { Icon: Users, label: "Ducks Active", value: d.count,      color: colors.info,   compact: true },
    { Icon: Egg,   label: "Duck Eggs",    value: d.eggsToday,  color: colors.accent, compact: true },
  ];

  const beeStats = [
    { Icon: Sprout,   label: "Bee Hives",     value: bees.hives,       color: colors.accent, compact: true },
    { Icon: Activity, label: "Honey Stored",  value: `${bees.honeyStored}kg`, color: colors.accent, compact: true },
  ];

  return (
    <ScreenWrapper title="Poultry & Duck">
      {/* Layer hens */}
      <Card>
        <SectionHeader Icon={Egg} title="800 Layer Hens" color={colors.poultry} />
        <StatGrid stats={henStats} />
      </Card>

      <View style={styles.gap} />

      {/* Ducks */}
      <Card>
        <SectionHeader Icon={Bug} title="Ducks — Pest Control" color={colors.info} />
        <StatGrid stats={duckStats} />
        <View style={styles.infoBox}>
          <Text style={styles.infoText}>
            <Text style={styles.bold}>Pest Control:</Text> {d.pestsConsumed} activity at {d.area}
          </Text>
        </View>
      </Card>

      <View style={styles.gap} />

      {/* Bees */}
      <Card>
        <SectionHeader Icon={Sprout} title="Apiculture — 20 Hives" color={colors.accent} />
        <StatGrid stats={beeStats} />
        <View style={styles.infoBox}>
          <Text style={styles.infoText}>Forager activity: {bees.activeForagers}</Text>
          <Text style={styles.infoText}>Last inspection: {bees.lastInspection}</Text>
          <Text style={styles.infoText}>Pollination boost: +18% greenhouse yield</Text>
        </View>
      </Card>
    </ScreenWrapper>
  );
}

const styles = StyleSheet.create({
  gap:     { height: spacing.lg },
  infoBox: { backgroundColor: colors.bg, borderRadius: radius.md, padding: spacing.md, marginTop: spacing.md },
  infoText:{ fontSize: fontSize.md, color: colors.textDim, lineHeight: 20 },
  bold:    { fontWeight: "600", color: colors.text },
});
