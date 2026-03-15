/**
 * Reports — multi-tab reporting dashboard for sales, production, financial, and store daily.
 */
import React, { useState, useEffect, useCallback } from "react";
import {
  View, Text, TouchableOpacity, ScrollView,
  StyleSheet, ActivityIndicator,
} from "react-native";
import { ClipboardList, TrendingUp, DollarSign, BarChart3, Store } from "lucide-react-native";
import ScreenWrapper from "../components/layout/ScreenWrapper";
import Card          from "../components/ui/Card";
import SectionHeader from "../components/ui/SectionHeader";
import StatGrid      from "../components/ui/StatGrid";
import Badge         from "../components/ui/Badge";
import { colors, spacing, radius, fontSize } from "../config/theme";
import { api }       from "../services/api";
import useAuthStore  from "../store/useAuthStore";

const TABS = [
  { key: "sales",      label: "Sales" },
  { key: "production", label: "Production" },
  { key: "financial",  label: "Financial" },
  { key: "store",      label: "Store Daily" },
];

export default function ReportsScreen() {
  const token = useAuthStore((s) => s.token);
  const [activeTab, setActiveTab] = useState("sales");
  const [data, setData]   = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState("");

  const fetchTab = useCallback(async (tab) => {
    setLoading(true); setError(""); setData(null);
    try {
      let result;
      switch (tab) {
        case "sales":      result = await api.reports.sales(token); break;
        case "production": result = await api.reports.production(token); break;
        case "financial":  result = await api.reports.financial(token); break;
        case "store":      result = await api.reports.storeDaily(token); break;
      }
      setData(result);
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  }, [token]);

  useEffect(() => { fetchTab(activeTab); }, [activeTab, fetchTab]);

  const switchTab = (tab) => { setActiveTab(tab); };

  return (
    <ScreenWrapper title="Reports">
      {/* Tab bar */}
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.tabBar} contentContainerStyle={styles.tabBarContent}>
        {TABS.map((t) => (
          <TouchableOpacity key={t.key} style={[styles.tab, activeTab === t.key && styles.tabActive]} onPress={() => switchTab(t.key)} activeOpacity={0.7}>
            <Text style={[styles.tabText, activeTab === t.key && styles.tabTextActive]}>{t.label}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {!!error && <View style={styles.errorBox}><Text style={styles.errorText}>{error}</Text></View>}

      {loading ? <ActivityIndicator size="large" color={colors.primary} style={{ marginTop: 40 }} /> : (
        <>
          {activeTab === "sales" && data && <SalesReport data={data} />}
          {activeTab === "production" && data && <ProductionReport data={data} />}
          {activeTab === "financial" && data && <FinancialReport data={data} />}
          {activeTab === "store" && data && <StoreDailyReport data={data} />}
          {!data && !loading && <Text style={styles.empty}>No report data available.</Text>}
        </>
      )}
    </ScreenWrapper>
  );
}

function SalesReport({ data }) {
  const stats = [
    { Icon: TrendingUp, label: "Total Revenue", value: `₹${(data.total_revenue ?? 0).toLocaleString()}`, color: colors.primary },
    { Icon: BarChart3,  label: "Transactions",  value: String(data.total_transactions ?? 0), color: colors.info },
    { Icon: DollarSign, label: "Avg Value",     value: `₹${(data.avg_transaction_value ?? 0).toFixed(0)}`, color: colors.accent },
  ];
  return (
    <>
      <StatGrid stats={stats} />
      <View style={{ height: spacing.lg }} />
      <Card>
        <SectionHeader Icon={TrendingUp} title="Top Products" color={colors.primary} />
        {(data.top_products ?? []).length === 0
          ? <Text style={styles.empty}>No sales data yet.</Text>
          : (data.top_products ?? []).map((p, i) => (
            <View key={i} style={styles.row}>
              <Text style={[styles.cell, { flex: 3 }]}>{p.product_name ?? p.product ?? "N/A"}</Text>
              <Text style={[styles.cell, { flex: 1, textAlign: "right" }]}>{p.quantity ?? 0}</Text>
              <Text style={[styles.cell, { flex: 2, textAlign: "right", color: colors.primary }]}>₹{(p.revenue ?? 0).toLocaleString()}</Text>
            </View>
          ))}
      </Card>
      {(data.by_payment_mode ?? []).length > 0 && (
        <>
          <View style={{ height: spacing.lg }} />
          <Card>
            <SectionHeader Icon={DollarSign} title="By Payment Mode" color={colors.accent} />
            {data.by_payment_mode.map((m, i) => (
              <View key={i} style={styles.row}>
                <Text style={[styles.cell, { flex: 2 }]}>{m.payment_mode}</Text>
                <Text style={[styles.cell, { flex: 1, textAlign: "right" }]}>{m.count}</Text>
                <Text style={[styles.cell, { flex: 2, textAlign: "right", color: colors.accent }]}>₹{(m.total ?? 0).toLocaleString()}</Text>
              </View>
            ))}
          </Card>
        </>
      )}
    </>
  );
}

function ProductionReport({ data }) {
  const stats = [
    { Icon: BarChart3,  label: "Total Batches",   value: String(data.total_batches ?? 0),    color: colors.crop },
    { Icon: DollarSign, label: "Total Value",      value: `₹${(data.total_value ?? 0).toLocaleString()}`, color: colors.primary },
  ];
  return (
    <>
      <StatGrid stats={stats} />
      <View style={{ height: spacing.lg }} />
      <Card>
        <SectionHeader Icon={BarChart3} title="By Category" color={colors.crop} />
        {(data.by_category ?? []).length === 0
          ? <Text style={styles.empty}>No production data.</Text>
          : (data.by_category ?? []).map((c, i) => (
            <View key={i} style={styles.row}>
              <Text style={[styles.cell, { flex: 2 }]}>{c.category}</Text>
              <Text style={[styles.cell, { flex: 1, textAlign: "right" }]}>{c.batches ?? c.count ?? 0}</Text>
              <Text style={[styles.cell, { flex: 2, textAlign: "right", color: colors.primary }]}>₹{(c.value ?? 0).toLocaleString()}</Text>
            </View>
          ))}
      </Card>
    </>
  );
}

function FinancialReport({ data }) {
  const stats = [
    { Icon: TrendingUp, label: "Revenue",  value: `₹${(data.total_revenue ?? 0).toLocaleString()}`,  color: colors.primary },
    { Icon: DollarSign, label: "Expenses", value: `₹${(data.total_expenses ?? 0).toLocaleString()}`, color: colors.danger },
    { Icon: DollarSign, label: "Profit",   value: `₹${(data.net_profit ?? 0).toLocaleString()}`,     color: colors.accent },
  ];
  return (
    <>
      <StatGrid stats={stats} />
      <View style={{ height: spacing.lg }} />
      {(data.revenue_streams ?? []).length > 0 && (
        <Card>
          <SectionHeader Icon={TrendingUp} title="Revenue Streams" color={colors.primary} />
          {data.revenue_streams.map((s, i) => (
            <View key={i} style={styles.row}>
              <Text style={[styles.cell, { flex: 3 }]}>{s.stream ?? s.category}</Text>
              <Text style={[styles.cell, { flex: 2, textAlign: "right", color: colors.primary }]}>₹{(s.total ?? s.amount ?? 0).toLocaleString()}</Text>
            </View>
          ))}
        </Card>
      )}
    </>
  );
}

function StoreDailyReport({ data }) {
  const stats = [
    { Icon: Store,      label: "Today Sales",    value: `₹${(data.total_sales ?? 0).toLocaleString()}`,         color: colors.store },
    { Icon: BarChart3,  label: "Transactions",   value: String(data.total_transactions ?? 0),                    color: colors.info },
    { Icon: DollarSign, label: "Cash In Hand",   value: `₹${(data.cash_in_hand ?? 0).toLocaleString()}`,        color: colors.accent },
    { Icon: TrendingUp, label: "Items Sold",     value: String(data.items_sold ?? 0),                            color: colors.primary },
  ];
  return (
    <>
      <StatGrid stats={stats} />
      <View style={{ height: spacing.lg }} />
      {data.top_product && (
        <Card>
          <SectionHeader Icon={Store} title="Top Product Today" color={colors.store} />
          <View style={{ padding: spacing.md }}>
            <Text style={{ color: colors.text, fontSize: fontSize.lg, fontWeight: "600" }}>{data.top_product}</Text>
          </View>
        </Card>
      )}
    </>
  );
}

const styles = StyleSheet.create({
  tabBar:          { flexGrow: 0, marginBottom: spacing.lg },
  tabBarContent:   { gap: spacing.sm },
  tab:             { paddingHorizontal: spacing.lg, paddingVertical: spacing.sm, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border },
  tabActive:       { borderColor: colors.reports, backgroundColor: colors.reports + "20" },
  tabText:         { fontSize: fontSize.md, color: colors.textDim, fontWeight: "600" },
  tabTextActive:   { color: colors.reports },
  errorBox:        { backgroundColor: colors.danger + "20", borderWidth: 1, borderColor: colors.danger + "40", borderRadius: radius.md, padding: spacing.md, marginBottom: spacing.md },
  errorText:       { color: colors.danger, fontSize: fontSize.md },
  empty:           { color: colors.textMuted, fontSize: fontSize.md, textAlign: "center", paddingVertical: 30 },
  row:             { flexDirection: "row", paddingVertical: spacing.sm, borderBottomWidth: 1, borderBottomColor: colors.border + "40", alignItems: "center" },
  cell:            { fontSize: fontSize.md, color: colors.text },
});
