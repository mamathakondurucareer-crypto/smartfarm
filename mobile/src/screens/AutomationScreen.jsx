import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { Droplets, Fish, Egg, RefreshCw, Thermometer, Wind } from "lucide-react-native";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import Card          from "../components/ui/Card";
import SectionHeader from "../components/ui/SectionHeader";
import Badge         from "../components/ui/Badge";
import { colors, spacing, radius, fontSize } from "../config/theme";
import useFarmStore  from "../store/useFarmStore";

const SYSTEM_META = {
  irrigation:    { Icon: Droplets,    name: "Irrigation System",    color: colors.water },
  fishFeeder:    { Icon: Fish,        name: "Fish Auto-Feeder",     color: colors.fish },
  eggBelt:       { Icon: Egg,         name: "Egg Collection Belt",  color: colors.poultry },
  manureScraper: { Icon: RefreshCw,   name: "Manure Scraper",       color: "#8B4513" },
  ghClimate:     { Icon: Thermometer, name: "Greenhouse Climate",   color: colors.crop },
  drone:         { Icon: Wind,        name: "Agriculture Drone",    color: colors.info },
};

function statusColor(status) {
  if (status === "Active" || status === "Running") return colors.primary;
  if (status === "Scheduled")                       return colors.accent;
  return colors.textMuted;
}

function systemDetails(key, data) {
  const details = {
    irrigation:    [`Zones: ${data.zonesActive}/${data.totalZones}`, `Last Run: ${data.lastRun}`],
    fishFeeder:    [`Next Feed: ${data.nextFeed}`, `Today: ${data.todayFeeds}/${data.totalFeeds} feeds`],
    eggBelt:       [`Collected: ${data.collected}/${data.target} eggs`, `Since: ${data.startTime}`],
    manureScraper: [`Next Run: ${data.nextRun}`, `Today: ${data.todayRuns}/${data.totalRuns} runs`],
    ghClimate:     [`Curtains: ${data.curtains}`, `Fans: ${data.fans} | Pad: ${data.pad}`],
    drone:         [`Battery: ${data.battery}%`, `Next Flight: ${data.nextScheduled}`],
  };
  return details[key] ?? [];
}

export default function AutomationScreen() {
  const automation = useFarmStore((s) => s.farm.automation);

  return (
    <ScreenWrapper title="Automation">
      {Object.entries(automation).map(([key, data]) => {
        const meta = SYSTEM_META[key];
        if (!meta) return null;

        return (
          <View key={key} style={styles.cardWrap}>
            <Card>
              <View style={styles.header}>
                <View style={styles.headerLeft}>
                  <View style={[styles.iconBox, { backgroundColor: meta.color + "22" }]}>
                    <meta.Icon size={18} color={meta.color} />
                  </View>
                  <View>
                    <Text style={styles.sysName}>{meta.name}</Text>
                    <Badge label={data.status} color={statusColor(data.status)} />
                  </View>
                </View>
                <View style={[styles.statusDot, { backgroundColor: statusColor(data.status) }]} />
              </View>

              <View style={styles.details}>
                {systemDetails(key, data).map((line, i) => (
                  <Text key={i} style={styles.detailLine}>{line}</Text>
                ))}
              </View>
            </Card>
          </View>
        );
      })}
    </ScreenWrapper>
  );
}

const styles = StyleSheet.create({
  cardWrap:   { marginBottom: spacing.md },
  header:     { flexDirection: "row", alignItems: "center", justifyContent: "space-between", marginBottom: spacing.md },
  headerLeft: { flexDirection: "row", alignItems: "center", gap: spacing.md },
  iconBox:    { width: 40, height: 40, borderRadius: radius.md, alignItems: "center", justifyContent: "center" },
  sysName:    { fontSize: fontSize.base, fontWeight: "700", color: colors.text, marginBottom: 4 },
  statusDot:  { width: 10, height: 10, borderRadius: 5 },
  details:    { gap: spacing.xs },
  detailLine: { fontSize: fontSize.sm, color: colors.textDim },
});
