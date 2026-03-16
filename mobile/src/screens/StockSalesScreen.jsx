/**
 * Stock Sales — sold inventory report with transaction history.
 */
import React, { useState, useEffect, useCallback } from "react";
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator,
} from "react-native";
import { TrendingUp, Filter, RefreshCw, DollarSign } from "lucide-react-native";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import Card          from "../components/ui/Card";
import SectionHeader from "../components/ui/SectionHeader";
import StatGrid      from "../components/ui/StatGrid";
import DataTable     from "../components/ui/DataTable";
import Badge         from "../components/ui/Badge";
import { colors, spacing, radius, fontSize } from "../config/theme";
import { api }       from "../services/api";
import useAuthStore  from "../store/useAuthStore";

export default function StockSalesScreen() {
  const token = useAuthStore((s) => s.token);

  const [salesData,  setSalesData]  = useState(null);
  const [txns,       setTxns]       = useState([]);
  const [loading,    setLoading]    = useState(true);
  const [error,      setError]      = useState("");
  const [startDate,  setStartDate]  = useState("");
  const [endDate,    setEndDate]    = useState("");

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const parts = [];
      if (startDate) parts.push(`start_date=${startDate}`);
      if (endDate)   parts.push(`end_date=${endDate}`);
      const params = parts.length ? "?" + parts.join("&") : "";
      const [s, t] = await Promise.all([
        api.reports.sales(token, params),
        api.pos.transactions(token, params),
      ]);
      setSalesData(s);
      setTxns(Array.isArray(t) ? t : t?.transactions ?? []);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [token, startDate, endDate]);

  useEffect(() => { fetchData(); }, []);

  const summary   = salesData?.summary ?? {};
  const totalRev  = summary.total_revenue ?? salesData?.total_revenue ?? 0;
  const txnCount  = summary.transaction_count ?? txns.length;
  const avgTxn    = txnCount > 0 ? totalRev / txnCount : 0;
  const topProd   = summary.top_product ?? salesData?.top_product ?? "—";

  const payModes  = salesData?.by_payment_mode ?? {};

  const stats = [
    { label: "Total Revenue",   value: `₹${Number(totalRev).toLocaleString()}`, color: colors.store,   icon: DollarSign },
    { label: "Transactions",    value: String(txnCount),                        color: colors.pos,     icon: TrendingUp },
    { label: "Avg Txn Value",   value: `₹${avgTxn.toFixed(0)}`,                color: colors.info,    icon: TrendingUp },
    { label: "Top Product",     value: topProd,                                 color: colors.primary, icon: TrendingUp },
  ];

  const txnHeaders = ["Date", "Code", "Items", "Total", "Payment", "Status"];
  const txnRows    = txns.map((t) => [
    (t.transaction_time ?? t.created_at) ? new Date(t.transaction_time ?? t.created_at).toLocaleDateString() : "—",
    t.transaction_code ?? t.id ?? "—",
    String(t.item_count ?? t.items?.length ?? 0),
    `₹${(t.total_amount ?? 0).toLocaleString()}`,
    <Badge key={`pm${t.id}`} label={t.payment_mode ?? "—"} color={colors.info} />,
    <Badge key={`st${t.id}`} label={t.status ?? "—"} color={t.status === "completed" ? colors.primary : colors.textMuted} />,
  ]);

  return (
    <ScreenWrapper title="Stock Sales">
      {!!error && (
        <View style={styles.errorBox}>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}

      {/* Filter */}
      <Card style={styles.cardGap}>
        <SectionHeader Icon={Filter} title="Date Range" color={colors.store} />
        <View style={styles.filterRow}>
          <View style={styles.filterField}>
            <Text style={styles.label}>Start Date</Text>
            <TextInput style={styles.input} value={startDate} onChangeText={setStartDate} placeholder="YYYY-MM-DD" placeholderTextColor={colors.textMuted} />
          </View>
          <View style={styles.filterField}>
            <Text style={styles.label}>End Date</Text>
            <TextInput style={styles.input} value={endDate} onChangeText={setEndDate} placeholder="YYYY-MM-DD" placeholderTextColor={colors.textMuted} />
          </View>
          <TouchableOpacity style={styles.refreshBtn} onPress={fetchData} activeOpacity={0.8}>
            <RefreshCw size={14} color={colors.bg} />
            <Text style={styles.refreshBtnText}>Apply</Text>
          </TouchableOpacity>
        </View>
      </Card>

      {loading ? (
        <ActivityIndicator size="large" color={colors.store} style={{ marginTop: 40 }} />
      ) : (
        <>
          <Card style={styles.cardGap}>
            <SectionHeader Icon={TrendingUp} title="Sales Summary" color={colors.store} />
            <StatGrid stats={stats} />
          </Card>

          {/* Payment mode breakdown */}
          {Object.keys(payModes).length > 0 && (
            <Card style={styles.cardGap}>
              <SectionHeader Icon={DollarSign} title="By Payment Mode" color={colors.pos} />
              <View style={styles.modeGrid}>
                {Object.entries(payModes).map(([mode, val]) => (
                  <View key={mode} style={styles.modeCard}>
                    <Badge label={mode} color={colors.info} />
                    <Text style={styles.modeVal}>₹{Number(val).toLocaleString()}</Text>
                  </View>
                ))}
              </View>
            </Card>
          )}

          <Card>
            <SectionHeader Icon={TrendingUp} title="Recent Transactions" color={colors.primary} />
            {txnRows.length === 0
              ? <Text style={styles.empty}>No transactions found</Text>
              : <DataTable headers={txnHeaders} rows={txnRows} />
            }
          </Card>
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
  refreshBtn:     { flexDirection: "row", alignItems: "center", gap: spacing.xs, backgroundColor: colors.store, borderRadius: radius.md, paddingHorizontal: spacing.md, paddingVertical: spacing.md, marginTop: spacing.lg },
  refreshBtnText: { color: colors.bg, fontWeight: "700", fontSize: fontSize.md },
  modeGrid:       { flexDirection: "row", flexWrap: "wrap", gap: spacing.md },
  modeCard:       { backgroundColor: colors.bg, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, padding: spacing.md, alignItems: "center", minWidth: 100 },
  modeVal:        { fontSize: fontSize.xl, color: colors.text, fontWeight: "700", marginTop: spacing.xs },
  empty:          { color: colors.textMuted, fontSize: fontSize.md, textAlign: "center", paddingVertical: spacing.lg },
});
