import React, { useEffect, useState } from "react";
import { View, Text } from "react-native";
import { Droplets, Fish, Egg, RefreshCw, Thermometer, Wind } from "lucide-react-native";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import Card          from "../components/ui/Card";
import SectionHeader from "../components/ui/SectionHeader";
import Badge         from "../components/ui/Badge";
import { colors, spacing, radius, fontSize } from "../config/theme";
import useFarmStore  from "../store/useFarmStore";
import useAuthStore  from "../store/useAuthStore";
import { api } from "../services/api";
import { styles } from "./AutomationScreen.styles";
import { commonStyles as cs } from "../styles/common";

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

// Map backend system names → frontend store keys
const BACKEND_KEY_MAP = {
  irrigation:  "irrigation",
  fish_feeder: "fishFeeder",
  egg_belt:    "eggBelt",
  gh_climate:  "ghClimate",
};

export default function AutomationScreen() {
  const automation = useFarmStore((s) => s.farm.automation);
  const token      = useAuthStore((s) => s.token);

  const [apiStatus, setApiStatus] = useState({});

  useEffect(() => {
    if (!token) return;
    api.automation.status(token)
      .then((data) => {
        // Remap backend keys to frontend keys
        const mapped = {};
        Object.entries(data).forEach(([backendKey, info]) => {
          const frontendKey = BACKEND_KEY_MAP[backendKey];
          if (frontendKey) {
            mapped[frontendKey] = info.enabled > 0 ? "Active" : info.total > 0 ? "Disabled" : "Idle";
          }
        });
        setApiStatus(mapped);
      })
      .catch(() => {});
  }, [token]);

  // Merge API status into local automation data
  const mergedAutomation = Object.fromEntries(
    Object.entries(automation).map(([key, data]) => [
      key,
      apiStatus[key] ? { ...data, status: apiStatus[key] } : data,
    ])
  );

  return (
    <ScreenWrapper title="Automation">
      {Object.entries(mergedAutomation).map(([key, data]) => {
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

