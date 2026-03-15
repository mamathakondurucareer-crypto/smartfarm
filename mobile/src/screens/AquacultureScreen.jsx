import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { Fish, Activity, Thermometer, Droplets, AlertTriangle, BarChart3 } from "lucide-react-native";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import StatGrid      from "../components/ui/StatGrid";
import Card          from "../components/ui/Card";
import SectionHeader from "../components/ui/SectionHeader";
import DataTable     from "../components/ui/DataTable";
import Badge         from "../components/ui/Badge";
import LineChartCard from "../components/charts/LineChartCard";
import { colors, spacing, fontSize } from "../config/theme";
import useFarmStore  from "../store/useFarmStore";

// Generate 24 hours of simulated water quality data
const waterQuality24hr = Array.from({ length: 24 }, (_, i) => ({
  hour: `${i}:00`,
  do:   +(5.5 + Math.sin(i / 4) * 1.2).toFixed(1),
  ph:   +(7.2 + Math.sin(i / 6) * 0.3).toFixed(2),
}));

export default function AquacultureScreen() {
  const farm = useFarmStore((s) => s.farm);
  const s    = farm.sensors;

  const totalStock   = farm.ponds.reduce((sum, p) => sum + p.stock, 0);
  const totalBiomass = farm.ponds.reduce((sum, p) => sum + p.stock * p.avgWeight, 0);

  const summaryStats = [
    { Icon: Fish,          label: "Total Stock",  value: totalStock.toLocaleString(), color: colors.fish,    sub: "6 ponds" },
    { Icon: Activity,      label: "Biomass",      value: `${(totalBiomass / 1000).toFixed(1)}T`, color: colors.primary },
    { Icon: Thermometer,   label: "Water Temp",   value: s.waterTemp,  unit: "°C",    color: colors.info },
    { Icon: Droplets,      label: "Avg DO",       value: s.dissolvedO2, unit: "mg/L", color: s.dissolvedO2 < 5 ? colors.danger : colors.water },
    { Icon: Activity,      label: "pH",           value: s.ph,                        color: colors.primary },
    { Icon: AlertTriangle, label: "Ammonia",      value: s.ammonia,    unit: "mg/L",  color: s.ammonia > 0.05 ? colors.danger : colors.primary },
  ];

  const tableHeaders = ["Pond", "Species", "Stock", "Wt (kg)", "FCR", "DO", "Feed (kg)", "Mort %"];
  const tableRows    = farm.ponds.map((p) => [
    <Text style={{ fontWeight: "700", color: colors.fish }}>{p.id}</Text>,
    p.species,
    p.stock.toLocaleString(),
    p.avgWeight.toFixed(2),
    p.fcr.toFixed(2),
    <Text style={{ color: p.do < 5 ? colors.danger : colors.primary, fontWeight: "600" }}>{p.do}</Text>,
    p.feedToday,
    <Text style={{ color: p.mortality > 2 ? colors.danger : colors.textDim }}>{p.mortality}%</Text>,
  ]);

  const wqHours   = waterQuality24hr.filter((_, i) => i % 3 === 0).map((d) => d.hour);
  const doValues  = waterQuality24hr.filter((_, i) => i % 3 === 0).map((d) => d.do);
  const phValues  = waterQuality24hr.filter((_, i) => i % 3 === 0).map((d) => d.ph);

  return (
    <ScreenWrapper title="Aquaculture">
      <StatGrid stats={summaryStats} />

      <View style={styles.gap} />

      {/* Pond table */}
      <Card>
        <SectionHeader Icon={Fish} title="Pond Status" color={colors.fish} />
        <DataTable headers={tableHeaders} rows={tableRows} />
      </Card>

      <View style={styles.gap} />

      {/* Water quality chart */}
      <LineChartCard
        Icon={Activity}
        title="Water Quality — 24 hr"
        color={colors.water}
        labels={wqHours}
        datasets={[
          { data: doValues, color: colors.water,  label: "DO (mg/L)" },
          { data: phValues, color: colors.accent,  label: "pH" },
        ]}
        height={220}
      />
    </ScreenWrapper>
  );
}

const styles = StyleSheet.create({
  gap: { height: spacing.lg },
});
