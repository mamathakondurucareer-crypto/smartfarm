import React from "react";
import { View, Text, TouchableOpacity } from "react-native";
import {
  DollarSign, TrendingUp, Fish, Egg, Sun, Droplets,
  Thermometer, Wind, Activity, AlertTriangle, Zap, BarChart3,
} from "lucide-react-native";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import StatGrid     from "../components/ui/StatGrid";
import Card         from "../components/ui/Card";
import SectionHeader from "../components/ui/SectionHeader";
import AlertDot     from "../components/ui/AlertDot";
import PieChartCard from "../components/charts/PieChartCard";
import { colors, spacing, radius, fontSize } from "../config/theme";
import useFarmStore  from "../store/useFarmStore";
import { styles } from "./DashboardScreen.styles";
import { commonStyles as cs } from "../styles/common";

// Revenue breakdown for the donut chart
const REVENUE_SEGMENTS = [
  { name: "Aquaculture",   value: 101.4, color: colors.fish },
  { name: "Greenhouse",    value: 19.05, color: colors.crop },
  { name: "Vertical Farm", value: 25,    color: colors.verticalFarm },
  { name: "Field Crops",   value: 60,    color: colors.accent },
  { name: "Poultry/Duck",  value: 33.8,  color: colors.poultry },
  { name: "Nursery",       value: 56.7,  color: colors.primary },
];

export default function DashboardScreen({ navigation }) {
  const farm = useFarmStore((s) => s.farm);
  const s    = farm.sensors;
  const f    = farm.financial;

  const totalFishStock = farm.ponds.reduce((sum, p) => sum + p.stock, 0);

  const kpiStats = [
    { Icon: DollarSign, label: "YTD Revenue",  value: `₹${f.ytdRevenue}L`,  color: colors.primary,  sub: "+12.4% vs target" },
    { Icon: TrendingUp, label: "YTD Profit",   value: `₹${f.ytdProfit}L`,   color: colors.accent,   sub: "65.1% margin" },
    { Icon: Fish,       label: "Fish Stock",   value: `${(totalFishStock / 1000).toFixed(1)}K`, color: colors.fish, sub: "6 ponds active" },
    { Icon: Egg,        label: "Eggs Today",   value: s.eggCount,            color: colors.poultry,  sub: `${farm.poultry.layRate}% lay rate` },
    { Icon: Sun,        label: "Solar Gen.",   value: `${s.solarGeneration}kW`, color: colors.solar, sub: `${s.gridExport}kW exported` },
    { Icon: Droplets,   label: "Reservoir",    value: `${s.reservoirLevel}%`, color: colors.water,  sub: "~7.8M litres" },
  ];

  const envStats = [
    { Icon: Thermometer, label: "Ambient",    value: s.ambientTemp,    unit: "°C",   color: colors.danger, compact: true },
    { Icon: Droplets,    label: "Humidity",   value: s.humidity,       unit: "%",    color: colors.water,  compact: true },
    { Icon: Wind,        label: "Wind",       value: s.windSpeed,      unit: "km/h", color: colors.textDim,compact: true },
    { Icon: Sun,         label: "Solar Rad.", value: s.solarRad,       unit: "W/m²", color: colors.solar,  compact: true },
    { Icon: Thermometer, label: "GH Temp",    value: s.ghTemp,         unit: "°C",   color: s.ghTemp > 36 ? colors.danger : colors.crop, compact: true },
    { Icon: Activity,    label: "GH CO₂",     value: s.ghCO2,          unit: "ppm",  color: colors.crop,   compact: true },
  ];

  return (
    <ScreenWrapper title="Dashboard">
      {/* KPI row */}
      <StatGrid stats={kpiStats} />

      <View style={cs.gap} />

      {/* Environment + Revenue pie */}
      <Card style={cs.cardGap}>
        <SectionHeader Icon={Thermometer} title="Environment" color={colors.info} />
        <StatGrid stats={envStats} />
      </Card>

      <View style={cs.gap} />

      <PieChartCard
        Icon={BarChart3}
        title="Revenue Mix (Annual Target)"
        color={colors.accent}
        segments={REVENUE_SEGMENTS}
        valuePrefix="₹"
        valueSuffix="L"
      />

      <View style={cs.gap} />

      {/* Alerts */}
      <Card style={cs.cardGap}>
        <SectionHeader Icon={AlertTriangle} title="Recent Alerts" color={colors.warn} />
        {farm.alerts.slice(0, 5).map((a) => (
          <View key={a.id} style={styles.alertRow}>
            <AlertDot type={a.type} />
            <View style={styles.alertBody}>
              <Text style={styles.alertMsg}>{a.msg}</Text>
              <Text style={styles.alertMeta}>{a.system} • {a.time}</Text>
            </View>
          </View>
        ))}
      </Card>

      <View style={cs.gap} />

      {/* Automation quick status */}
      <Card>
        <SectionHeader Icon={Zap} title="Automation Status" color={colors.danger} />
        <View style={styles.autoGrid}>
          {Object.entries(farm.automation).map(([key, val]) => {
            const isActive = val.status === "Active" || val.status === "Running";
            const dotColor = isActive ? colors.primary : val.status === "Scheduled" ? colors.accent : colors.textMuted;
            return (
              <TouchableOpacity
                key={key}
                style={styles.autoItem}
                onPress={() => navigation.navigate("Automation")}
                activeOpacity={0.7}
              >
                <View style={[styles.autoDot, { backgroundColor: dotColor }]} />
                <View>
                  <Text style={styles.autoName}>{key.replace(/([A-Z])/g, " $1")}</Text>
                  <Text style={styles.autoStatus}>{val.status}</Text>
                </View>
              </TouchableOpacity>
            );
          })}
        </View>
      </Card>
    </ScreenWrapper>
  );
}

