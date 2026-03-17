/**
 * SensorZoneScreen — View sensor readings by zone.
 * Zones: Ponds, Greenhouse, Vertical Farm, Field
 */
import React, { useState, useEffect, useCallback } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  RefreshControl,
} from "react-native";
import { Droplets, Leaf, Sprout, TrendingUp } from "lucide-react-native";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import Card from "../components/ui/Card";
import { colors, spacing, radius, fontSize } from "../config/theme";
import { api } from "../services/api";
import useAuthStore from "../store/useAuthStore";
import { styles } from "./SensorZoneScreen.styles";
import { commonStyles as cs } from "../styles/common";

const ZONES = [
  { id: "ponds", label: "Ponds", Icon: Droplets },
  { id: "greenhouse", label: "Greenhouse", Icon: Leaf },
  { id: "vertical_farm", label: "Vertical Farm", Icon: Sprout },
  { id: "field", label: "Field", Icon: TrendingUp },
];

const ZONE_COLORS = {
  ponds: colors.water,
  greenhouse: colors.crop,
  vertical_farm: colors.verticalFarm,
  field: colors.accent,
};

export default function SensorZoneScreen() {
  const token = useAuthStore((s) => s.token);
  const [selectedZone, setSelectedZone] = useState("ponds");
  const [devices, setDevices] = useState([]);
  const [readings, setReadings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const [devicesResp, readingsResp] = await Promise.all([
        api.sensors.devices(token, `?zone=${selectedZone}`),
        api.sensors.latestByZone(selectedZone, token),
      ]);
      setDevices(Array.isArray(devicesResp) ? devicesResp : []);
      setReadings(Array.isArray(readingsResp) ? readingsResp : []);
    } catch (e) {
      console.error("Error fetching sensor data:", e);
    } finally {
      setLoading(false);
    }
  }, [token, selectedZone]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await fetchData();
    setRefreshing(false);
  }, [fetchData]);

  const getSensorReading = (deviceId) => {
    return readings.find((r) => r.device_id === deviceId);
  };

  return (
    <ScreenWrapper title="Sensor Zones">
      {/* Zone selector buttons */}
      <View style={cs.chipRow}>
        {ZONES.map((zone) => {
          const isActive = selectedZone === zone.id;
          return (
            <TouchableOpacity
              key={zone.id}
              style={[cs.chip, isActive && cs.chipActive]}
              onPress={() => setSelectedZone(zone.id)}
            >
              <Text style={[cs.chipText, isActive && cs.chipActiveText]}>
                {zone.label}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>

      <View style={cs.gap} />

      {loading ? (
        <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
          <ActivityIndicator size="large" color={colors.primary} />
        </View>
      ) : devices.length === 0 ? (
        <View style={cs.emptyState}>
          <Droplets size={48} color={colors.textMuted} />
          <Text style={cs.emptyTitle}>No sensors in this zone</Text>
          <Text style={cs.emptyText}>Configure sensors for {selectedZone}</Text>
        </View>
      ) : (
        <ScrollView
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        >
          {devices.map((device) => {
            const reading = getSensorReading(device.id);
            return (
              <Card key={device.id} style={cs.cardGap}>
                <View style={styles.deviceHeader}>
                  <Text style={styles.deviceName}>{device.name}</Text>
                  <View
                    style={[
                      styles.statusBadge,
                      {
                        backgroundColor:
                          device.is_active === false
                            ? colors.danger
                            : colors.primary,
                      },
                    ]}
                  >
                    <Text style={styles.statusText}>
                      {device.is_active === false ? "Offline" : "Online"}
                    </Text>
                  </View>
                </View>

                {reading ? (
                  <>
                    <View style={styles.readingRow}>
                      <Text style={styles.readingLabel}>{reading.parameter_name}</Text>
                      <Text style={styles.readingValue}>
                        {reading.value} {reading.unit}
                      </Text>
                    </View>
                    <Text style={styles.readingTime}>
                      Last updated: {new Date(reading.timestamp).toLocaleString()}
                    </Text>
                  </>
                ) : (
                  <Text style={cs.empty}>No reading available</Text>
                )}
              </Card>
            );
          })}
        </ScrollView>
      )}
    </ScreenWrapper>
  );
}
