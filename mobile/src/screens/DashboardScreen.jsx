import React, { useEffect, useState } from "react";
import { View, Text, TouchableOpacity } from "react-native";
import {
  DollarSign, TrendingUp, Fish, Egg, Sun, Droplets,
  Thermometer, Wind, Activity, AlertTriangle, Zap, BarChart3, WifiOff,
} from "lucide-react-native";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import StatGrid     from "../components/ui/StatGrid";
import Card         from "../components/ui/Card";
import SectionHeader from "../components/ui/SectionHeader";
import AlertDot     from "../components/ui/AlertDot";
import PieChartCard from "../components/charts/PieChartCard";
import { colors, spacing, radius, fontSize } from "../config/theme";
import useFarmStore  from "../store/useFarmStore";
import useAuthStore  from "../store/useAuthStore";
import { api } from "../services/api";
import { styles } from "./DashboardScreen.styles";
import { commonStyles as cs } from "../styles/common";

const STREAM_COLORS = {
  aquaculture:   colors.fish,
  greenhouse:    colors.crop,
  vertical_farm: colors.verticalFarm,
  field_crops:   colors.accent,
  poultry:       colors.poultry,
  nursery:       colors.primary,
};

export default function DashboardScreen({ navigation }) {
  const farm  = useFarmStore((s) => s.farm);
  const token = useAuthStore((s) => s.token);
  const s     = farm.sensors;

  const [kpis, setKpis] = useState(null);
  const [revenueSegments, setRevenueSegments] = useState([]);
  const [apiAlerts, setApiAlerts] = useState([]);
  const [staleData, setStaleData] = useState(false);

  useEffect(() => {
    if (!token) return;
    const now = new Date();
    const start = `${now.getFullYear()}-01-01`;
    const end   = now.toISOString().slice(0, 10);
    api.dashboard.kpis(token, `?start_date=${start}&end_date=${end}`)
      .then(setKpis)
      .catch(() => setStaleData(true));
    api.dashboard.revenueByStream(token, `?start_date=${start}&end_date=${end}`)
      .then((rows) => {
        const segs = rows.map((r) => ({
          name:  r.stream.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()),
          value: +(r.total / 100000).toFixed(2),
          color: STREAM_COLORS[r.stream] || colors.textDim,
        }));
        if (segs.length) setRevenueSegments(segs);
      })
      .catch(() => setStaleData(true));
    api.sensors.alerts(token, "?resolved=false&limit=5")
      .then((rows) => {
        const mapped = rows.map((a) => ({
          id:     a.id,
          type:   a.alert_type,
          msg:    a.message,
          time:   new Date(a.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          system: a.source_system || a.category,
        }));
        setApiAlerts(mapped);
      })
      .catch(() => setStaleData(true));
  }, [token]);

  // Use API alerts when available, fall back to simulated local alerts
  const displayAlerts = apiAlerts.length > 0 ? apiAlerts : farm.alerts.slice(0, 5);

  const revenue    = kpis ? (kpis.financial.revenue   / 100000).toFixed(1) : "—";
  const profit     = kpis ? (kpis.financial.profit    / 100000).toFixed(1) : "—";
  const margin     = kpis ? kpis.financial.margin_pct : null;
  const fishStock  = kpis ? kpis.aquaculture.total_stock : null;
  const activePonds= kpis ? kpis.aquaculture.active_ponds : null;
  const eggsToday  = kpis ? kpis.poultry.eggs_today : null;
  const layRate    = kpis ? kpis.poultry.lay_rate_pct : null;

  const kpiStats = [
    { Icon: DollarSign, label: "YTD Revenue",  value: `₹${revenue}L`,  color: colors.primary,
      sub: margin !== null ? `${margin}% margin` : "no data yet" },
    { Icon: TrendingUp, label: "YTD Profit",   value: `₹${profit}L`,   color: colors.accent,
      sub: margin !== null ? `${margin}% margin` : "no data yet" },
    { Icon: Fish,       label: "Fish Stock",
      value: fishStock !== null ? fishStock >= 1000 ? `${(fishStock/1000).toFixed(1)}K` : String(fishStock) : "—",
      color: colors.fish,
      sub: activePonds !== null ? `${activePonds} ponds active` : "no ponds" },
    { Icon: Egg,        label: "Eggs Today",
      value: eggsToday !== null ? String(eggsToday) : "—",
      color: colors.poultry,
      sub: layRate ? `${layRate}% lay rate` : "no flock" },
    { Icon: Sun,        label: "Solar Gen.",   value: `${s.solarGeneration}kW`, color: colors.solar, sub: `${s.gridExport}kW exported` },
    { Icon: Droplets,   label: "Reservoir",    value: `${s.reservoirLevel}%`,   color: colors.water, sub: "~7.8M litres" },
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
      {staleData && (
        <View style={cs.warnBox}>
          <WifiOff size={14} color={colors.warn} />
          <Text style={cs.warnText}>Live data unavailable — showing cached data</Text>
        </View>
      )}

      {/* KPI row */}
      <StatGrid stats={kpiStats} />

      <View style={cs.gap} />

      {/* Environment + Revenue pie */}
      <Card style={cs.cardGap}>
        <SectionHeader Icon={Thermometer} title="Environment" color={colors.info} />
        <StatGrid stats={envStats} />
      </Card>

      <View style={cs.gap} />

      {revenueSegments.length > 0 && (
        <PieChartCard
          Icon={BarChart3}
          title="Revenue Mix (YTD)"
          color={colors.accent}
          segments={revenueSegments}
          valuePrefix="₹"
          valueSuffix="L"
        />
      )}

      <View style={cs.gap} />

      {/* Alerts */}
      <Card style={cs.cardGap}>
        <SectionHeader Icon={AlertTriangle} title="Recent Alerts" color={colors.warn} />
        {displayAlerts.map((a) => (
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

