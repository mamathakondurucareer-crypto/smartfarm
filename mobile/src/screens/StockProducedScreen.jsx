/**
 * Stock Produced — farm production output report.
 */
import React, { useState, useEffect, useCallback } from "react";
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator,
} from "react-native";
import { Layers, RefreshCw, Filter } from "lucide-react-native";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import Card          from "../components/ui/Card";
import SectionHeader from "../components/ui/SectionHeader";
import StatGrid      from "../components/ui/StatGrid";
import DataTable     from "../components/ui/DataTable";
import Badge         from "../components/ui/Badge";
import { colors, spacing, radius, fontSize } from "../config/theme";
import { api }       from "../services/api";
import useAuthStore  from "../store/useAuthStore";

export default function StockProducedScreen() {
  const token = useAuthStore((s) => s.token);

  const [data,       setData]       = useState(null);
  const [loading,    setLoading]    = useState(true);
  const [error,      setError]      = useState("");
  const [startDate,  setStartDate]  = useState("");
  const [endDate,    setEndDate]    = useState("");

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      let params = "";
      const parts = [];
      if (startDate) parts.push(`start_date=${startDate}`);
      if (endDate)   parts.push(`end_date=${endDate}`);
      if (parts.length) params = "?" + parts.join("&");
      const result = await api.reports.production(token, params);
      setData(result);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [token, startDate, endDate]);

  useEffect(() => { fetchData(); }, []);

  const totalBatches = data?.total_batches ?? 0;
  const totalVal     = data?.total_value ?? 0;
  const byCategory   = data?.by_category ?? {};
  const bySource     = data?.by_source ?? {};
  const topCat       = Object.keys(byCategory).length > 0
    ? Object.entries(byCategory).sort((a, b) => b[1] - a[1])[0][0]
    : "—";

  const stats = [
    { label: "Total Batches",  value: String(totalBatches),                      color: colors.primary,  icon: Layers },
    { label: "Total Value",    value: `₹${Number(totalVal).toLocaleString()}`,   color: colors.store,    icon: Layers },
    { label: "Top Category",   value: topCat,                                    color: colors.packing,  icon: Layers },
  ];

  const headers = ["Category", "Quantity"];
  const rows    = Object.entries(byCategory).map(([cat, qty]) => [
    cat,
    String(qty),
  ]);

  return (
    <ScreenWrapper title="Stock Produced">
      {!!error && (
        <View style={styles.errorBox}>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}

      {/* Filter row */}
      <Card style={styles.cardGap}>
        <SectionHeader Icon={Filter} title="Date Filter" color={colors.packing} />
        <View style={styles.filterRow}>
          <View style={styles.filterField}>
            <Text style={styles.label}>Start Date</Text>
            <TextInput
              style={styles.input}
              value={startDate}
              onChangeText={setStartDate}
              placeholder="YYYY-MM-DD"
              placeholderTextColor={colors.textMuted}
            />
          </View>
          <View style={styles.filterField}>
            <Text style={styles.label}>End Date</Text>
            <TextInput
              style={styles.input}
              value={endDate}
              onChangeText={setEndDate}
              placeholder="YYYY-MM-DD"
              placeholderTextColor={colors.textMuted}
            />
          </View>
          <TouchableOpacity style={styles.refreshBtn} onPress={fetchData} activeOpacity={0.8}>
            <RefreshCw size={14} color={colors.bg} />
            <Text style={styles.refreshBtnText}>Refresh</Text>
          </TouchableOpacity>
        </View>
      </Card>

      {loading ? (
        <ActivityIndicator size="large" color={colors.packing} style={{ marginTop: 40 }} />
      ) : (
        <>
          <Card style={styles.cardGap}>
            <SectionHeader Icon={Layers} title="Production Summary" color={colors.packing} />
            <StatGrid stats={stats} />
          </Card>

          <Card style={styles.cardGap}>
            <SectionHeader Icon={Layers} title="By Category" color={colors.primary} />
            {rows.length === 0
              ? <Text style={styles.empty}>No production records found</Text>
              : <DataTable headers={headers} rows={rows} />
            }
          </Card>

          {Object.keys(bySource).length > 0 && (
            <Card>
              <SectionHeader Icon={Layers} title="By Source" color={colors.store} />
              <DataTable headers={["Source", "Quantity"]} rows={Object.entries(bySource).map(([src, qty]) => [src, String(qty)])} />
            </Card>
          )}
        </>
      )}
    </ScreenWrapper>
  );
}

const styles = StyleSheet.create({
  errorBox:       { backgroundColor: colors.danger + "20", borderWidth: 1, borderColor: colors.danger + "40", borderRadius: radius.md, padding: spacing.md, marginBottom: spacing.md },
  errorText:      { color: colors.danger, fontSize: fontSize.md },
  cardGap:        { marginBottom: spacing.md },
  filterRow:      { flexDirection: "row", gap: spacing.sm, alignItems: "flex-end", flexWrap: "wrap" },
  filterField:    { flex: 1, minWidth: 120 },
  label:          { fontSize: fontSize.md, color: colors.textDim, marginBottom: spacing.xs },
  input:          { backgroundColor: colors.bg, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, padding: spacing.md, color: colors.text, fontSize: fontSize.base },
  refreshBtn:     { flexDirection: "row", alignItems: "center", gap: spacing.xs, backgroundColor: colors.packing, borderRadius: radius.md, paddingHorizontal: spacing.md, paddingVertical: spacing.md, marginTop: spacing.lg },
  refreshBtnText: { color: colors.bg, fontWeight: "700", fontSize: fontSize.md },
  empty:          { color: colors.textMuted, fontSize: fontSize.md, textAlign: "center", paddingVertical: spacing.lg },
});
