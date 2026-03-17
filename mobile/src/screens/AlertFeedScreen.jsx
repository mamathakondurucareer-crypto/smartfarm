/**
 * AlertFeedScreen — Active alerts and historical records.
 * Tabs: Active, History
 */
import React, { useState, useEffect, useCallback } from "react";
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
} from "react-native";
import { AlertTriangle, CheckCircle } from "lucide-react-native";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import Card from "../components/ui/Card";
import { colors, spacing, radius, fontSize } from "../config/theme";
import { api } from "../services/api";
import useAuthStore from "../store/useAuthStore";
import { styles } from "./AlertFeedScreen.styles";
import { commonStyles as cs } from "../styles/common";

const SEVERITY_COLORS = {
  CRITICAL: colors.danger,
  HIGH: colors.warn,
  MEDIUM: colors.accent,
  LOW: colors.info,
};

export default function AlertFeedScreen() {
  const token = useAuthStore((s) => s.token);
  const [tab, setTab] = useState("active"); // active, history
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchAlerts = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const resolved = tab === "history";
      const rows = await api.sensors.alerts(token, `?resolved=${resolved}&limit=50`);
      const mapped = (rows || []).map((a) => ({
        id: a.id,
        severity: (a.alert_type || "MEDIUM").toUpperCase(),
        module: a.source_system || a.category || "System",
        message: a.message,
        timestamp: new Date(a.created_at).toLocaleString(),
        createdAt: a.created_at,
      }));
      setAlerts(mapped);
    } catch (e) {
      console.error("Error fetching alerts:", e);
    } finally {
      setLoading(false);
    }
  }, [token, tab]);

  useEffect(() => {
    fetchAlerts();
  }, [fetchAlerts]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await fetchAlerts();
    setRefreshing(false);
  }, [fetchAlerts]);

  const handleResolveAlert = async (alertId) => {
    try {
      await api.sensors.resolveAlert(alertId, token);
      fetchAlerts();
    } catch (e) {
      console.error("Error resolving alert:", e);
    }
  };

  const renderAlertCard = ({ item }) => (
    <Card style={cs.cardGap}>
      <View style={styles.alertHeader}>
        <View
          style={[styles.severityBadge, { backgroundColor: SEVERITY_COLORS[item.severity] }]}
        >
          <Text style={styles.severityText}>{item.severity}</Text>
        </View>
        <Text style={styles.module}>{item.module}</Text>
      </View>

      <Text style={styles.message}>{item.message}</Text>
      <Text style={styles.timestamp}>{item.timestamp}</Text>

      {tab === "active" && (
        <TouchableOpacity
          style={[cs.saveButton, { marginTop: spacing.md }]}
          onPress={() => handleResolveAlert(item.id)}
        >
          <Text style={cs.saveButtonText}>Mark Resolved</Text>
        </TouchableOpacity>
      )}
    </Card>
  );

  return (
    <ScreenWrapper title="Alerts">
      {/* Tab bar */}
      <View style={cs.tabBar}>
        {["active", "history"].map((t) => (
          <TouchableOpacity
            key={t}
            style={[cs.tab, tab === t && cs.tabActive]}
            onPress={() => setTab(t)}
          >
            <Text style={[cs.tabText, tab === t && cs.tabActiveText]}>
              {t === "active" ? "Active" : "History"}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {loading ? (
        <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
          <ActivityIndicator size="large" color={colors.primary} />
        </View>
      ) : alerts.length === 0 ? (
        <View style={cs.emptyState}>
          <CheckCircle size={48} color={colors.textMuted} />
          <Text style={cs.emptyTitle}>
            {tab === "active" ? "No active alerts" : "No history"}
          </Text>
          <Text style={cs.emptyText}>
            {tab === "active" ? "All systems operating normally" : "No resolved alerts yet"}
          </Text>
        </View>
      ) : (
        <FlatList
          data={alerts}
          keyExtractor={(item) => String(item.id)}
          renderItem={renderAlertCard}
          scrollEnabled={false}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        />
      )}
    </ScreenWrapper>
  );
}
