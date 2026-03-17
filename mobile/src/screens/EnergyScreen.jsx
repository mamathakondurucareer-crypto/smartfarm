import React, { useEffect, useMemo, useState } from "react";
import { View } from "react-native";
import { Sun, Zap, TrendingUp, DollarSign, BarChart3 } from "lucide-react-native";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import StatGrid      from "../components/ui/StatGrid";
import LineChartCard from "../components/charts/LineChartCard";
import { colors, spacing } from "../config/theme";
import useFarmStore  from "../store/useFarmStore";
import useAuthStore  from "../store/useAuthStore";
import { api } from "../services/api";
import { styles } from "./EnergyScreen.styles";
import { commonStyles as cs } from "../styles/common";

// Simulated 24-hour solar profile (every 2 hours for readability)
function buildHourlyProfile() {
  return Array.from({ length: 13 }, (_, i) => {
    const hour = i * 2;
    const gen  = hour < 6 || hour > 18 ? 0 : Math.max(0, 120 * Math.sin(((hour - 6) / 12) * Math.PI));
    const cons = 50 + Math.random() * 30;
    return {
      label:      `${hour}h`,
      generation: +gen.toFixed(1),
      consumption: +cons.toFixed(1),
      export:     +Math.max(0, gen - cons).toFixed(1),
    };
  });
}

export default function EnergyScreen() {
  const farm    = useFarmStore((s) => s.farm);
  const token   = useAuthStore((s) => s.token);
  const s       = farm.sensors;
  const hourly  = useMemo(buildHourlyProfile, []);

  const [apiEnergy, setApiEnergy] = useState(null);

  useEffect(() => {
    if (!token) return;
    api.sensors.energySummary(token).then(setApiEnergy).catch(() => {});
  }, [token]);

  const solarGeneration = apiEnergy?.solarGeneration ?? s.solarGeneration;
  const farmConsumption = apiEnergy?.farmConsumption ?? s.farmConsumption;
  const gridExport      = apiEnergy?.gridExport      ?? s.gridExport;

  const kpiStats = [
    { Icon: Sun,       label: "Current Gen",   value: solarGeneration, unit: "kW", color: colors.solar, sub: "of 120 kWp capacity" },
    { Icon: Zap,       label: "Consumption",   value: farmConsumption, unit: "kW", color: colors.info },
    { Icon: TrendingUp,label: "Grid Export",   value: gridExport,      unit: "kW", color: colors.primary },
    { Icon: DollarSign,label: "Today Revenue", value: "₹1,234",                    color: colors.accent, sub: "Grid export earnings" },
  ];

  return (
    <ScreenWrapper title="Solar Energy">
      <StatGrid stats={kpiStats} />

      <View style={cs.gap} />

      <LineChartCard
        Icon={BarChart3}
        title="24-Hour Energy Profile"
        color={colors.solar}
        labels={hourly.map((h) => h.label)}
        datasets={[
          { data: hourly.map((h) => h.generation),  color: colors.solar,   label: "Generation (kW)" },
          { data: hourly.map((h) => h.consumption),  color: colors.info,    label: "Consumption (kW)" },
          { data: hourly.map((h) => h.export),        color: colors.primary, label: "Export (kW)" },
        ]}
        height={260}
      />
    </ScreenWrapper>
  );
}

