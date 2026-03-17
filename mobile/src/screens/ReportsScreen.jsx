/**
 * Reports — multi-tab reporting dashboard for sales, production, financial, and store daily.
 */
import React, { useState, useEffect, useCallback } from "react";
import {
  View, Text, TouchableOpacity, ScrollView,
  ActivityIndicator,
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
import { styles } from "./ReportsScreen.styles";
import { commonStyles as cs } from "../styles/common";

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

      {!!error && <View style={cs.errorBox}><Text style={cs.errorText}>{error}</Text></View>}

      {loading ? <ActivityIndicator size="large" color={colors.primary} style={{ marginTop: 40 }} /> : (
        <>
          {activeTab === "sales" && data && <SalesReport data={data} />}
          {activeTab === "production" && data && <ProductionReport data={data} />}
          {activeTab === "financial" && data && <FinancialReport data={data} />}
          {activeTab === "store" && data && <StoreDailyReport data={data} />}
          {!data && !loading && <Text style={cs.empty}>No report data available.</Text>}
        </>
      )}
    </ScreenWrapper>
  );
}

function SalesReport({ data }) {
  const stats = [
    { Icon: TrendingUp, label: "Total Revenue", value: `₹${Number(data.total_revenue ?? 0).toLocaleString()}`, color: colors.primary },
    { Icon: BarChart3,  label: "Transactions",  value: String(data.total_transactions ?? 0), color: colors.info },
    { Icon: DollarSign, label: "Avg Value",     value: `₹${Number(data.avg_transaction_value ?? 0).toFixed(0)}`, color: colors.accent },
  ];
  return (
    <>
      <StatGrid stats={stats} />
      <View style={{ height: spacing.lg }} />
      <Card>
        <SectionHeader Icon={TrendingUp} title="Top Products" color={colors.primary} />
        {(data.top_products ?? []).length === 0
          ? <Text style={cs.empty}>No sales data yet.</Text>
          : (data.top_products ?? []).map((p, i) => (
            <View key={i} style={cs.row}>
              <Text style={[styles.cell, { flex: 3 }]}>{p.product_name ?? "N/A"}</Text>
              <Text style={[styles.cell, { flex: 1, textAlign: "right" }]}>{p.qty_sold ?? p.quantity ?? 0}</Text>
              <Text style={[styles.cell, { flex: 2, textAlign: "right", color: colors.primary }]}>₹{Number(p.revenue ?? 0).toLocaleString()}</Text>
            </View>
          ))}
      </Card>
      {data.by_payment_mode && Object.keys(data.by_payment_mode).length > 0 && (
        <>
          <View style={{ height: spacing.lg }} />
          <Card>
            <SectionHeader Icon={DollarSign} title="By Payment Mode" color={colors.accent} />
            {Object.entries(data.by_payment_mode).map(([mode, total], i) => (
              <View key={i} style={styles.row}>
                <Text style={[styles.cell, { flex: 2 }]}>{mode}</Text>
                <Text style={[styles.cell, { flex: 2, textAlign: "right", color: colors.accent }]}>₹{(total ?? 0).toLocaleString()}</Text>
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
        {!data.by_category || Object.keys(data.by_category).length === 0
          ? <Text style={cs.empty}>No production data.</Text>
          : Object.entries(data.by_category).map(([category, qty], i) => (
            <View key={i} style={cs.row}>
              <Text style={[styles.cell, { flex: 2 }]}>{category}</Text>
              <Text style={[styles.cell, { flex: 2, textAlign: "right", color: colors.primary }]}>{Number(qty ?? 0).toFixed(2)}</Text>
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
    { Icon: DollarSign, label: "Profit",   value: `₹${(data.gross_profit ?? 0).toLocaleString()}`,     color: colors.accent },
  ];
  return (
    <>
      <StatGrid stats={stats} />
      <View style={{ height: spacing.lg }} />
      {data.revenue_streams && Object.keys(data.revenue_streams).length > 0 && (
        <Card>
          <SectionHeader Icon={TrendingUp} title="Revenue Streams" color={colors.primary} />
          {Object.entries(data.revenue_streams).map(([stream, total], i) => (
            <View key={i} style={cs.row}>
              <Text style={[styles.cell, { flex: 3 }]}>{stream}</Text>
              <Text style={[styles.cell, { flex: 2, textAlign: "right", color: colors.primary }]}>₹{(total ?? 0).toLocaleString()}</Text>
            </View>
          ))}
        </Card>
      )}
    </>
  );
}

function StoreDailyReport({ data }) {
  const stats = [
    { Icon: Store,      label: "Today Sales",    value: `₹${Number(data.total_sales ?? 0).toLocaleString()}`,         color: colors.store },
    { Icon: BarChart3,  label: "Transactions",   value: String(data.total_transactions ?? 0),                          color: colors.info },
    { Icon: DollarSign, label: "Cash In Hand",   value: `₹${Number(data.cash_in_hand ?? 0).toLocaleString()}`,        color: colors.accent },
    { Icon: TrendingUp, label: "Items Sold",     value: String(Math.round(data.items_sold ?? 0)),                      color: colors.primary },
  ];
  return (
    <>
      <StatGrid stats={stats} />
      <View style={{ height: spacing.lg }} />
      {data.top_product && (
        <Card style={{ marginBottom: spacing.lg }}>
          <SectionHeader Icon={Store} title="Top Product Today" color={colors.store} />
          <View style={{ padding: spacing.md }}>
            <Text style={{ color: colors.text, fontSize: fontSize.lg, fontWeight: "600" }}>{data.top_product}</Text>
            {data.top_product_revenue > 0 && (
              <Text style={{ color: colors.store, fontSize: fontSize.md, marginTop: 4 }}>₹{Number(data.top_product_revenue).toLocaleString()}</Text>
            )}
          </View>
        </Card>
      )}
      {data.payment_breakdown && Object.keys(data.payment_breakdown).length > 0 && (
        <Card>
          <SectionHeader Icon={DollarSign} title="Payment Breakdown" color={colors.accent} />
          {Object.entries(data.payment_breakdown).map(([mode, total], i) => (
            <View key={i} style={cs.row}>
              <Text style={[styles.cell, { flex: 2, textTransform: "capitalize" }]}>{mode}</Text>
              <Text style={[styles.cell, { flex: 2, textAlign: "right", color: colors.accent }]}>₹{Number(total ?? 0).toLocaleString()}</Text>
            </View>
          ))}
        </Card>
      )}
    </>
  );
}

